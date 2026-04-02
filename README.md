# 述格 (ScriptGrid)

[English](docs/README_EN.md) | 中文

![Python Version](https://img.shields.io/badge/Python-3.13+-blue.svg)
![Framework](https://img.shields.io/badge/Framework-FastAPI-green.svg)
![Deployment](https://img.shields.io/badge/Deploy-Docker-blue.svg)
![License](https://img.shields.io/badge/License-MIT-brightgreen.svg)

**专为口述影像创作者打造的轻量级在线口述稿格式转换工具。**

[**在线体验 (Live Demo)**](#-在线体验) | [**快速开始**](#-快速开始) | [**部署指南**](#-本地部署与开发)

---

## 📖 项目简介

在口述影像创作团队协作中，经常需要在**字幕格式（如 .ass, .srt）**与**表格格式（.xlsx）**之间进行转换。手动转换不仅效率低下，还容易出错，影响创作流程。

**述格 (ScriptGrid)** 是一个基于 Web 的格式转换工具，旨在帮助口述影像创作者、译者和团队成员轻松、快速地在不同格式的口述稿之间进行转换，从而极大地提升协同创作的效率。

### 核心优势

- 🌐 **无需安装** - 通过浏览器即可直接使用
- ⚡ **快速转换** - 高效的转换引擎，带来极速的转换体验
- 🎯 **专业定制** - 专为口述影像创作场景设计
- ♿ **无障碍友好** - 完整支持键盘操作和屏幕阅读器
- 🔒 **隐私保护** - 文件处理后会立刻被服务端销毁，绝无泄露风险

## ✨ 主要功能

### 🔄 多向文件转换

- **字幕转表格**: 将 `.ass` 和 `.srt` 格式转换为结构化的 `.xlsx` 表格
- **表格转字幕**: 将标准格式的 `.xlsx` 表格转换为 `.srt` 格式
- **字幕格式互转**: 将 `.ass` 格式转换为更通用的 `.srt` 格式
- **SUP PGS 支持**: 将 `.sup` 格式的图像字幕转换为 `.srt` 或 `.xlsx` 格式
- **空白口述稿自动打轴**: 基于影片的对白字幕（支持 SRT/ASS/SUP 格式），自动分析出没有对白的空白时间段，为口述影像工作者生成口述稿字幕时间轴模板

### ⚙️ 智能识别与提取

- 自动识别文件类型并动态显示可用的转换选项
- 精确提取字幕文件中的**序号、开始时间、结束时间、字幕内容**等关键信息
- 支持从 `.ass` 文件中剥离特效标签，保留纯净的文本内容
- **SUP 图像识别**: 使用 TorchfreeEasyOCR + ONNX Runtime 技术自动识别 SUP 格式中的图像字幕
- **语言智能检测**: 自动检测字幕语言（中文/英文/混合），优化 OCR 识别效果

### 🌐 现代 Web 体验

- **响应式设计**: 界面自适应桌面、平板和手机等不同设备
- **直观操作**: 拖拽上传文件，一键完成转换
- **实时反馈**: 转换进度提示和结果预览

## 🚀 在线体验

您可以直接访问下面的网址，立即开始使用：

**[https://sg.kadaiad.fun:4680/](https://sg.kadaiad.fun:4680/)**

## 🏃 快速开始

### 使用步骤

1. **选择文件**: 点击"选择字幕文件"按钮，上传您的文件（支持 .ass, .srt, .xlsx, .sup 格式）
2. **选择转换类型**: 系统会自动识别文件类型并显示可用的转换选项
3. **开始转换**: 点击"开始转换"按钮
4. **下载结果**: 转换完成后，文件会自动下载到您的设备

### 支持的转换类型

| 输入格式 | 输出格式 | 说明 |
|---------|---------|------|
| .ass | .srt | ASS 字幕转 SRT 格式 |
| .ass | .xlsx | ASS 字幕转 Excel 表格 |
| .srt | .xlsx | SRT 字幕转 Excel 表格 |
| .xlsx | .srt | Excel 表格转 SRT 字幕 |
| .sup | .srt | SUP PGS 字幕转 SRT 格式 |
| .sup | .xlsx | SUP PGS 字幕转 Excel 表格 |
| .srt/.ass/.sup | .srt | 空白口述稿自动打轴，生成带占位符的口述稿字幕 |

### 空白口述稿自动打轴

**使用方式：**
1. 上传对白字幕文件（支持 SRT/ASS/SUP 格式）
2. 选择"空白口述稿自动打轴"
3. 自动生成带占位符文本的 SRT 口述稿字幕

**技术细节：**
- 口述稿字幕与前后对白保持 500ms 间隔
- 单条口述稿最短 1 秒，最长不限制。

## 🛠️ 技术架构

本项目采用前后端分离的现代化 Web 架构，通过 Docker 进行容器化部署。

### 技术栈

**后端 (Backend)**
- **语言**: Python 3.13+
- **框架**: [FastAPI](https://fastapi.tiangolo.com/) - 高性能异步 Web 框架
- **服务器**: [Uvicorn](https://www.uvicorn.org/) - ASGI 服务器
- **核心库**: [openpyxl](https://openpyxl.readthedocs.io/) - Excel 文件处理
- **OCR 识别**: [TorchfreeEasyOCR](https://github.com/SeldonHZ/TorchfreeEasyOCR) + ONNX Runtime - 高性能图像文字识别

**前端 (Frontend)**
- **基础**: HTML5, CSS3, JavaScript (ES6+)
- **UI 框架**: [Bootstrap 5](https://getbootstrap.com/) - 响应式界面框架

**部署 (Deployment)**
- **容器化**: [Docker](https://www.docker.com/) - 一键部署和运行

### 项目结构

```
ScriptGrid/
├── app.py                 # FastAPI 主程序入口
├── constants.py           # 全局常量定义
├── exceptions.py          # 统一异常处理
├── parsers.py            # 字幕文件解析器
├── writers.py            # 文件写入器
├── subtitle_converter.py # 核心转换逻辑
├── pgsreader.py          # SUP PGS 文件解析器
├── imagemaker.py         # 图像处理模块
├── static/               # 静态资源
│   └── index.html        # 前端页面
├── templates/            # 模板文件
├── Dockerfile            # Docker 构建文件
├── requirements.txt      # Python 依赖
└── README.md            # 项目文档
```

## 🏡 本地部署与开发

### 环境要求

- Python 3.13 或更高版本
- pip (Python 包管理器)
- Docker (可选，用于容器化部署)

### 方法一：Python 直接运行 (开发环境)

1. **克隆仓库**
   ```bash
   git clone https://github.com/yunshenwuji/scriptgrid.git
   cd scriptgrid
   ```

2. **创建虚拟环境** (推荐)
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **启动服务**
   ```bash
   python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```
   
   > `--reload` 参数使服务在代码变动后自动重启，适合开发环境

5. **访问应用**
   
   打开浏览器访问 `http://127.0.0.1:8000`

### 方法二：Docker 部署 (生产环境)

1. **克隆仓库** (如果尚未克隆)
   ```bash
   git clone https://github.com/yunshenwuji/scriptgrid.git
   cd scriptgrid
   ```

2. **构建 Docker 镜像**
   ```bash
   docker build -t scriptgrid:latest .
   ```

3. **运行 Docker 容器**
   ```bash
   docker run -d -p 8000:8000 --name scriptgrid-app scriptgrid:latest
   ```
   
   参数说明：
   - `-d`: 后台运行容器
   - `-p 8000:8000`: 端口映射（主机:容器）
   - `--name scriptgrid-app`: 容器名称

4. **查看运行状态**
   ```bash
   docker ps
   ```

5. **访问应用**
   
   打开浏览器访问 `http://127.0.0.1:8000`

### 停止服务

**Python 方式**: 在终端中按 `Ctrl+C`

**Docker 方式**:
```bash
# 停止容器
docker stop scriptgrid-app

# 删除容器
docker rm scriptgrid-app
```

## 🤝 贡献指南

我们欢迎社区贡献！如果您有好的想法或发现了问题，请通过以下方式参与：

### 报告问题

如果您在使用过程中遇到问题，请：
1. 在 [GitHub Issues](https://github.com/yunshenwuji/scriptgrid/issues) 中搜索是否已有相关问题
2. 如果没有，请创建新的 Issue，详细描述问题和复现步骤

### 提交代码

1. **Fork** 本仓库到您的 GitHub 账号
2. 创建功能分支：`git checkout -b feature/AmazingFeature`
3. 提交代码：`git commit -m 'Add some AmazingFeature'`
4. 推送分支：`git push origin feature/AmazingFeature`
5. 提交 **Pull Request**

### 开发建议

- 在提交代码前，请先创建 Issue 讨论您的想法
- 遵循现有的代码风格和命名规范
- 为新功能添加相应的测试
- 更新相关文档

## 📝 更新日志

### v1.1.0 (Latest)
- ✨ 新增 SUP PGS 字幕格式支持
- ✨ 集成 EasyOCR 技术，支持图像字幕识别
- ✨ 自动语言检测，优化中英文字幕识别
- ✨ 支持 .sup 转 .srt 和 .sup 转 .xlsx 格式

### v1.0.0
- ✨ 支持 .ass/.srt 转 .xlsx 格式
- ✨ 支持 .xlsx 转 .srt 格式
- ✨ 支持 .ass 转 .srt 格式
- 🌐 响应式 Web 界面
- ♿ 无障碍访问支持
- 🐳 Docker 容器化部署

## 📄 许可证

本项目采用 MIT 许可证。详情请见 [LICENSE](LICENSE) 文件。

## 💬 联系我们

- 项目主页: [https://github.com/yunshenwuji/scriptgrid](https://github.com/yunshenwuji/scriptgrid)
- 问题反馈: [GitHub Issues](https://github.com/yunshenwuji/scriptgrid/issues)
- 在线体验: [https://sg.kadaiad.fun:4680/](https://sg.kadaiad.fun:4680/)

## 💰 支持项目

如果喜欢述格，欢迎捐赠  
支付宝或微信扫码请我喝杯咖啡

<div align="center">
  <img src="static/PayQrcode.png" alt="支付宝微信收款二维码" width="200">
</div>

---

⭐ 如果这个项目对您有帮助，请给我们一个星标支持！