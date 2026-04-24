# 述格 (ScriptGrid) 前端自动化测试脚本需求文档

## 1. 概述

### 1.1 目的

基于 Playwright CLI 工具，编写一个可重复执行的前端自动化测试脚本，通过 Edge 浏览器模拟用户操作，对述格的所有转换功能进行端到端验证，并自动对比输出结果与预期文件。

### 1.2 适用范围

本脚本覆盖述格 Web 端所有 9 种转换路径的自动化测试，包括同步转换和异步（SUP）转换。

---

## 2. 测试矩阵

| 编号 | 输入文件 | 转换类型 | 预期输出文件 | 转换模式 |
|------|---------|---------|-------------|---------|
| T01 | test/ass/input.ass | ass_to_srt | test/ass/output.srt | 同步 |
| T02 | test/ass/input.ass | subtitle_to_excel | test/ass/output.xlsx | 同步 |
| T03 | test/ass/input.ass | auto_narration_timing | test/ass/narration_output.srt | 同步 |
| T04 | test/srt/input.srt | subtitle_to_excel | test/srt/output.xlsx | 同步 |
| T05 | test/srt/input.srt | auto_narration_timing | test/srt/narration_output.srt | 同步 |
| T06 | test/xlsx/input.xlsx | xlsx_to_srt | test/xlsx/output.srt | 同步 |
| T07 | test/sup/input.sup | sup_to_srt | test/sup/output.srt | 异步 |
| T08 | test/sup/input.sup | sup_to_excel | test/sup/output.xlsx | 异步 |
| T09 | test/sup/input.sup | auto_narration_timing | test/sup/narration_output.srt | 异步 |

---

## 3. 环境要求

| 项目 | 要求 |
|------|------|
| 后端服务 | 运行在 `http://127.0.0.1:8000`，脚本启动前需确认服务可用 |
| 浏览器 | Microsoft Edge，无头模式（默认） |
| Python | 使用项目虚拟环境 `ScriptGrid/Scripts/python.exe`（含 openpyxl 依赖） |
| Node.js | 需安装 `playwright-cli`（`npm install -g @playwright/cli@latest`） |

---

## 4. 技术方案

### 4.1 脚本语言

使用 **PowerShell 脚本**（`.ps1`），因为：
- 项目运行在 Windows 环境
- 可直接调用 `playwright-cli` 命令
- 可调用 Python 对比脚本
- 支持条件判断、循环、输出格式化

### 4.2 浏览器操作方案

#### 4.2.1 启动浏览器

```powershell
playwright-cli open --browser=msedge http://127.0.0.1:8000
```

#### 4.2.2 文件上传

**禁止使用** `playwright-cli upload` 命令（受沙箱限制会报 "File access denied" 错误）。

**必须使用** `run-code` 通过 Playwright API 直接设置文件：

```powershell
playwright-cli run-code "async page => { await page.locator('input[type=file]').setInputFiles('C:\ScriptGrid\test\{subdir}\input.{ext}'); return 'file set'; }"
```

#### 4.2.3 选择转换类型

```powershell
playwright-cli select e15 "{conversion_type_value}"
```

#### 4.2.4 同步转换的下载捕获

同步转换（ASS/SRT/XLSX）使用 `waitForEvent('download')` 拦截下载并保存到指定路径：

```powershell
playwright-cli run-code "async page => {
  const downloadPromise = page.waitForEvent('download');
  await page.getByRole('button', { name: '开始处理' }).click();
  const download = await downloadPromise;
  await download.saveAs('C:\ScriptGrid\test\actual_output.{ext}');
  return download.suggestedFilename();
}"
```

#### 4.2.5 异步转换（SUP）的完成检测与下载捕获

SUP 转换是异步的，不能直接用 `waitForEvent('download')`。需要轮询页面状态：

```powershell
playwright-cli run-code "async page => {
  await page.getByRole('button', { name: '开始处理' }).click();
  const maxWait = 600000;  # 最长等待10分钟
  const start = Date.now();
  while (Date.now() - start < maxWait) {
    await page.waitForTimeout(5000);
    const success = await page.locator('.alert-success').count();
    const error = await page.locator('.alert-danger').count();
    if (success > 0) return 'SUCCESS';
    if (error > 0) return 'ERROR: ' + await page.locator('.alert-danger').textContent();
  }
  return 'TIMEOUT';
}"
```

SUP 转换完成后文件自动下载到 `.playwright-cli/` 目录，需从该目录复制到 test 目录进行对比。

#### 4.2.6 页面重置

每次转换完成后，需要重新加载页面以确保控件状态干净：

```powershell
playwright-cli run-code "async page => { await page.reload(); await page.waitForLoadState('networkidle'); return 'reloaded'; }"
```

> **踩坑记录**：SUP 异步转换完成后，如果直接在下一次测试中设置文件和选择类型，会遇到下拉框 `disabled` 的问题。必须先 reload 页面。

### 4.3 文件对比方案

使用已有的 `test/compare.py` 脚本，通过项目虚拟环境的 Python 执行：

```powershell
c:\ScriptGrid\ScriptGrid\Scripts\python.exe "c:\ScriptGrid\test\compare.py" "<实际输出>" "<预期输出>"
```

脚本返回退出码：
- `0`：文件一致（输出含 "✅"）
- `1`：文件不一致或有错误（输出含 "❌"）

---

## 5. 脚本流程

```
开始
 │
 ├─ 检查后端服务是否可用（HTTP GET http://127.0.0.1:8000）
 │   └─ 不可用则报错退出
 │
 ├─ 启动 Edge 浏览器（无头模式）
 │
 ├─ 逐项执行测试矩阵（T01-T09）
 │   ├─ reload 页面
 │   ├─ 上传输入文件
 │   ├─ 选择转换类型
 │   ├─ 提交转换
 │   │   ├─ 同步转换：waitForEvent('download') → saveAs
 │   │   └─ 异步转换：轮询 .alert-success → 从 .playwright-cli/ 复制文件
 │   ├─ 运行 compare.py 对比输出
 │   └─ 记录结果（通过/失败/差异详情）
 │
 ├─ 关闭浏览器
 │
 └─ 输出测试报告
```

---

## 6. 输出格式

### 6.1 控制台实时输出

每个测试项执行时输出：

```
[T01] ASS→SRT ... 上传文件 ... 选择转换类型 ... 提交转换 ... 下载完成 ... 对比结果: ✅ 通过
[T07] SUP→SRT ... 上传文件 ... 选择转换类型 ... 提交转换 ... 等待完成(125s) ... 下载完成 ... 对比结果: ✅ 通过
```

### 6.2 最终测试报告

```
============================
 述格前端自动化测试报告
============================
执行时间: 2026-04-15 23:50:00
总用例数: 9
通过: 8
失败: 1

详细结果:
  T01 ASS→SRT           ✅ 通过
  T02 ASS→Excel         ✅ 通过
  T03 ASS口述稿打轴      ✅ 通过
  T04 SRT→Excel         ✅ 通过
  T05 SRT口述稿打轴      ✅ 通过
  T06 XLSX→SRT          ✅ 通过
  T07 SUP→SRT           ✅ 通过
  T08 SUP→Excel         ❌ 失败 (3702处差异)
  T09 SUP口述稿打轴      ✅ 通过

BUG 列表:
  BUG-001: SUP→Excel 输出与预期不一致
    - 时间戳从 00:00:03 开始 vs 预期 00:03:41 开始
    - 字幕内容为迪士尼片头 vs 预期港片对白
============================
```

---

## 7. 踩坑与注意事项

| # | 坑点 | 解决方案 |
|---|------|---------|
| 1 | `playwright-cli upload` 报 File access denied | 改用 `run-code` + `setInputFiles()` |
| 2 | 默认无头模式下运行自动化测试 | 无需额外参数，playwright-cli 默认即为无头模式 |
| 3 | SUP 异步转换不能直接 waitForEvent('download') | 改为轮询 `.alert-success` 出现 |
| 4 | SUP 下载文件不进入系统 Downloads 目录 | 从 `.playwright-cli/` 目录复制 |
| 5 | 系统Python无openpyxl | 使用项目venv中的Python |
| 6 | SUP转换后控件未恢复，下拉框disabled | 每次测试前 reload 页面 |
| 7 | run-code 中 PowerShell 对引号转义敏感 | 双引号内使用反引号或单引号转义 |

---

## 8. 文件结构

```
test/
├── ass/
│   ├── input.ass
│   ├── output.srt
│   ├── output.xlsx
│   └── narration_output.srt
├── srt/
│   ├── input.srt
│   ├── output.xlsx
│   └── narration_output.srt
├── sup/
│   ├── input.sup
│   ├── output.srt
│   ├── output.xlsx
│   └── narration_output.srt
├── xlsx/
│   ├── input.xlsx
│   └── output.srt
├── compare.py              # 文件对比工具
├── frontend_test.md        # 手工测试文档
└── run_test.ps1            # 自动化测试脚本（待开发）
```
