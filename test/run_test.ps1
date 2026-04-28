#!/usr/bin/env pwsh
# ============================================================
# ScriptGrid 前端自动化测试脚本
# 基于 playwright-cli + Edge 浏览器（无头模式）
# ============================================================

$ErrorActionPreference = 'Continue'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# ===== 配置区 =====
$BaseUrl = 'http://127.0.0.1:8000'
# 自动根据脚本所在位置推导路径，避免在不同 Windows 开发机上因绝对路径写死而失效
# 约定脚本位于 <项目根>\test\run_test.ps1
$TestDir = $PSScriptRoot
$ProjectDir = Split-Path -Parent $PSScriptRoot
$PythonExe = Join-Path $ProjectDir 'ScriptGrid\Scripts\python.exe'
$PwDir = Join-Path $TestDir '.playwright-cli'
$TemplateDir = Join-Path $TestDir 'templates'

# ===== 测试用例 =====
$TestCases = @(
    @{ Id='T01'; Input='ass\input.ass';       Type='ass_to_srt';            Expected='ass\output.srt';           Mode='sync';  Label='ASS-SRT'       }
    @{ Id='T02'; Input='ass\input.ass';       Type='subtitle_to_excel';     Expected='ass\output.xlsx';          Mode='sync';  Label='ASS-Excel'     }
    @{ Id='T03'; Input='ass\input.ass';       Type='auto_narration_timing'; Expected='ass\narration_output.srt'; Mode='sync';  Label='ASS-Narration' }
    @{ Id='T04'; Input='srt\input.srt';       Type='subtitle_to_excel';     Expected='srt\output.xlsx';          Mode='sync';  Label='SRT-Excel'     }
    @{ Id='T05'; Input='srt\input.srt';       Type='auto_narration_timing'; Expected='srt\narration_output.srt'; Mode='sync';  Label='SRT-Narration' }
    @{ Id='T06'; Input='xlsx\input.xlsx';     Type='xlsx_to_srt';           Expected='xlsx\output.srt';          Mode='sync';  Label='XLSX-SRT'      }
    @{ Id='T07'; Input='sup\input.sup';       Type='sup_to_srt';            Expected='sup\input.srt';            Mode='async'; Label='SUP-SRT'       }
    @{ Id='T08'; Input='sup\input.sup';       Type='sup_to_excel';          Expected='sup\input.xlsx';           Mode='async'; Label='SUP-Excel'     }
    @{ Id='T09'; Input='sup\input.sup';       Type='auto_narration_timing'; Expected='sup\narration_input.srt';  Mode='async'; Label='SUP-Narration' }
)

# ===== 结果存储 =====
$script:Results = @()
$script:PassCount = 0
$script:FailCount = 0

# ===== 加载 JS 模板 =====
$SyncJsTemplate = Get-Content (Join-Path $TemplateDir 'sync_test.js') -Raw -Encoding UTF8
$AsyncJsTemplate = Get-Content (Join-Path $TemplateDir 'async_test.js') -Raw -Encoding UTF8

# ===== 辅助函数 =====

function Write-Color($text, $color) {
    Write-Host $text -ForegroundColor $color
}

function Write-Step($msg) {
    Write-Host $msg -NoNewline
}

function Check-Backend {
    # 禁用进度条，避免其绘制/清除动作与上一条 -NoNewline 输出的中文宽字符
    # 发生重绘冲突，导致 "检查后端服务 ..." 行出现字符重复或错位的回显异常
    $prevProgress = $ProgressPreference
    $ProgressPreference = 'SilentlyContinue'
    try {
        $null = Invoke-WebRequest -Uri $BaseUrl -Method GET -TimeoutSec 5 -UseBasicParsing
        return $true
    } catch {
        return $false
    } finally {
        $ProgressPreference = $prevProgress
    }
}

function Run-PlaywrightCode($jsCode) {
    $result = & playwright-cli run-code $jsCode 2>&1
    $output = $result | Out-String
    return $output
}

function Get-ActualFilePath {
    param($TestId, $ExpectedPath)
    $ext = [System.IO.Path]::GetExtension($ExpectedPath)
    return Join-Path $TestDir "actual_${TestId}_output${ext}"
}

function To-JsPath($path) {
    # 将 Windows 反斜杠路径转换为 JavaScript 使用的正斜杠
    return $path -replace '\\', '/'
}

function Build-JsCode($template, $inputPath, $convType, $outputPath) {
    # 替换模板中的占位符，使用正斜杠路径
    $jsInput = To-JsPath $inputPath
    $jsOutput = To-JsPath $outputPath
    $code = $template
    $code = $code -replace '\{\{INPUT_PATH\}\}', $jsInput
    $code = $code -replace '\{\{CONV_TYPE\}\}', $convType
    $code = $code -replace '\{\{OUTPUT_PATH\}\}', $jsOutput
    return $code
}

function Compare-TestOutput {
    param($ActualPath, $ExpectedPath)
    if (-not (Test-Path $ActualPath)) {
        return @{ Success = $false; Detail = 'Actual file not found: ' + $ActualPath }
    }
    if (-not (Test-Path $ExpectedPath)) {
        return @{ Success = $false; Detail = 'Expected file not found: ' + $ExpectedPath }
    }

    $compareScript = Join-Path $TestDir 'compare.py'
    $compareOutput = & $PythonExe $compareScript $ActualPath $ExpectedPath --quiet 2>&1 | Out-String
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0 -and $compareOutput -match 'PASS\|') {
        return @{ Success = $true; Detail = '' }
    } else {
        # 从精简输出中提取详细信息
        $detail = $compareOutput.Trim()
        if ($compareOutput -match 'FAIL\|(.+)') {
            $detail = $Matches[1].Trim()
        } elseif ([string]::IsNullOrWhiteSpace($detail)) {
            $detail = '未知对比错误'
        }
        return @{ Success = $false; Detail = $detail }
    }
}

# ===== 同步测试函数 =====
function Run-SyncTest {
    param($tc)
    $inputPath = Join-Path $ProjectDir ('test\' + $tc.Input)
    $expectedPath = Join-Path $TestDir $tc.Expected
    $actualPath = Get-ActualFilePath $tc.Id $expectedPath

    Write-Step ' ...'

    $jsCode = Build-JsCode $SyncJsTemplate $inputPath $tc.Type $actualPath

    try {
        $output = Run-PlaywrightCode $jsCode

        # 检测真正的 JavaScript 错误，而非任何包含 'error' 的文本
        if ($output -match '^### Error' -or $output -match 'SyntaxError:|TypeError:|ReferenceError:') {
            Write-Host ' 失败' -ForegroundColor Red
            Write-Host ''
            $script:FailCount++
            $detail = $output.Substring(0, [Math]::Min(200, $output.Length)).Trim()
            $script:Results += @{ Id=$tc.Id; Label=$tc.Label; Status='FAIL'; Detail=('转换失败: ' + $detail) }
            return
        }

        # 检测超时
        if ($output -match '^\s*TIMEOUT\s*$' -or $output -match 'TimeoutError') {
            Write-Host ' 失败 (超时)' -ForegroundColor Red
            Write-Host ''
            $script:FailCount++
            $script:Results += @{ Id=$tc.Id; Label=$tc.Label; Status='FAIL'; Detail='转换超时' }
            return
        }

        if (-not (Test-Path $actualPath)) {
            Write-Host ' 失败 (未找到下载文件)' -ForegroundColor Red
            Write-Host ''
            $script:FailCount++
            $script:Results += @{ Id=$tc.Id; Label=$tc.Label; Status='FAIL'; Detail=('下载文件未保存: ' + $actualPath) }
            return
        }

        Write-Host -NoNewline ' 对比中...'

        $cmp = Compare-TestOutput $actualPath $expectedPath
        if ($cmp.Success) {
            Write-Host ' 通过' -ForegroundColor Green
        } else {
            Write-Host ' 失败' -ForegroundColor Red
            $script:FailCount++
            $script:Results += @{ Id=$tc.Id; Label=$tc.Label; Status='FAIL'; Detail=$cmp.Detail }
            return
        }
    } catch {
        $errMsg = $_.Exception.Message
        Write-Host (' 异常: ' + $errMsg) -ForegroundColor Red
        $script:FailCount++
        $script:Results += @{ Id=$tc.Id; Label=$tc.Label; Status='FAIL'; Detail=$errMsg }
        return
    }

    $script:PassCount++
    $script:Results += @{ Id=$tc.Id; Label=$tc.Label; Status='PASS'; Detail='' }
}

# ===== 异步 SUP 测试函数 =====
function Run-AsyncTest {
    param($tc)
    $inputPath = Join-Path $ProjectDir ('test\' + $tc.Input)
    $expectedPath = Join-Path $TestDir $tc.Expected
    $actualPath = Get-ActualFilePath $tc.Id $expectedPath

    Write-Step ' ... (异步，最长 10 分钟)'

    $testStartTime = Get-Date

    # 清理 .playwright-cli/ 中的旧下载文件
    if (Test-Path $PwDir) {
        Get-ChildItem $PwDir -File | Where-Object { $_.Extension -in '.srt','.xlsx' } |
            Remove-Item -Force -ErrorAction SilentlyContinue
    }

    $jsCode = Build-JsCode $AsyncJsTemplate $inputPath $tc.Type ''

    try {
        $output = Run-PlaywrightCode $jsCode

        if ($output -match 'ERROR:') {
            $errorMsg = '未知错误'
            # 只检查 Result 部分，不检查代码片段
            # 从 ### Result 行提取直到下一个 ### 部分
            $resultMatch = [regex]::Match($output, '### Result\s*\n"([^"]+)"', [System.Text.RegularExpressions.RegexOptions]::Singleline)
            if ($resultMatch.Success) {
                $resultValue = $resultMatch.Groups[1].Value
                if ($resultValue -match '^ERROR:\s*(.+)') {
                    $errorMsg = $Matches[1].Trim()
                }
            }
            
            # 如果找到真正的 ERROR 结果，则测试失败
            if ($errorMsg -ne '未知错误') {
                Write-Host (' 失败: ' + $errorMsg) -ForegroundColor Red
                Write-Host ''
                $script:FailCount++
                $script:Results += @{ Id=$tc.Id; Label=$tc.Label; Status='FAIL'; Detail=('转换错误: ' + $errorMsg) }
                return
            }
        }

        # 检查 Result 中的 TIMEOUT
        $resultMatch = [regex]::Match($output, '### Result\s*\n"([^"]+)"', [System.Text.RegularExpressions.RegexOptions]::Singleline)
        if ($resultMatch.Success -and $resultMatch.Groups[1].Value -eq 'TIMEOUT') {
            Write-Host ' 失败 (超时 10分钟)' -ForegroundColor Red
            Write-Host ''
            $script:FailCount++
            $script:Results += @{ Id=$tc.Id; Label=$tc.Label; Status='FAIL'; Detail='转换超时' }
            return
        }

        # 从 Result 中提取耗时
        $elapsed = ''
        if ($resultMatch.Success -and $resultMatch.Groups[1].Value -match '^SUCCESS:(\d+s)') {
            $elapsed = ' (' + $Matches[1] + ')'
        }

        Write-Host -NoNewline (' 完成' + $elapsed + ' 对比中...')

        # 在 .playwright-cli/ 中查找下载的文件
        $ext = [System.IO.Path]::GetExtension($expectedPath)
        $downloadedFile = $null
        $waitCount = 0
        while ($waitCount -lt 30) {
            Start-Sleep -Milliseconds 1000
            $downloadedFile = Get-ChildItem $PwDir -File |
                Where-Object { $_.Extension -eq $ext -and $_.LastWriteTime -gt $testStartTime } |
                Sort-Object LastWriteTime -Descending |
                Select-Object -First 1
            if ($downloadedFile) { break }
            $waitCount++
        }

        if (-not $downloadedFile) {
            Write-Host ' 失败 (未找到下载文件)' -ForegroundColor Red
            Write-Host ''
            $script:FailCount++
            $script:Results += @{ Id=$tc.Id; Label=$tc.Label; Status='FAIL'; Detail=('未在 ' + $PwDir + ' 中找到下载文件') }
            return
        }

        Copy-Item $downloadedFile.FullName $actualPath -Force

        $cmp = Compare-TestOutput $actualPath $expectedPath
        if ($cmp.Success) {
            Write-Host ' 通过' -ForegroundColor Green
        } else {
            Write-Host ' 失败' -ForegroundColor Red
            $script:FailCount++
            $script:Results += @{ Id=$tc.Id; Label=$tc.Label; Status='FAIL'; Detail=$cmp.Detail }
            return
        }
    } catch {
        $errMsg = $_.Exception.Message
        Write-Host (' 异常: ' + $errMsg) -ForegroundColor Red
        $script:FailCount++
        $script:Results += @{ Id=$tc.Id; Label=$tc.Label; Status='FAIL'; Detail=$errMsg }
        return
    }

    $script:PassCount++
    $script:Results += @{ Id=$tc.Id; Label=$tc.Label; Status='PASS'; Detail='' }
}

# ===== 打印测试报告 =====
function Print-Report {
    Write-Host ''
    Write-Host '============================' -ForegroundColor Cyan
    Write-Host ' ScriptGrid 测试报告' -ForegroundColor Cyan
    Write-Host '============================' -ForegroundColor Cyan
    Write-Host ('时间: ' + (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'))
    Write-Host ('总计: ' + $TestCases.Count)
    Write-Host ('通过: ' + $script:PassCount) -ForegroundColor Green -NoNewline
    Write-Host ('  失败: ' + $script:FailCount) -ForegroundColor Red
    Write-Host ''
    Write-Host '详细信息:'

    foreach ($r in $script:Results) {
        $icon = if ($r.Status -eq 'PASS') { [char]0x2705 } else { [char]0x274C }
        $label = ($r.Id + ' ' + $r.Label).PadRight(22)
        $statusText = if ($r.Status -eq 'PASS') { '通过' } else { '失败' }

        Write-Host ('  ' + $label + ' ' + $icon + ' ' + $statusText) -NoNewline
        if ($r.Status -eq 'FAIL' -and -not [string]::IsNullOrWhiteSpace($r.Detail)) {
            $shortDetail = $r.Detail.Substring(0, [Math]::Min(100, $r.Detail.Length))
            Write-Host (' (' + $shortDetail + ')') -ForegroundColor Yellow
        } else {
            Write-Host ''
        }
    }

    # BUG 列表
    $failResults = $script:Results | Where-Object { $_.Status -eq 'FAIL' }
    if ($failResults) {
        Write-Host ''
        Write-Host 'BUG 列表:' -ForegroundColor Red
        $bugNum = 1
        foreach ($r in $failResults) {
            Write-Host ('  BUG-' + $bugNum.ToString('000') + ': [' + $r.Id + '] ' + $r.Label) -ForegroundColor Red
            if (-not [string]::IsNullOrWhiteSpace($r.Detail)) {
                $splitPattern = '; '
                $lines = $r.Detail -split $splitPattern | Select-Object -First 3
                foreach ($line in $lines) {
                    Write-Host ('    - ' + $line.Trim()) -ForegroundColor Yellow
                }
            }
            $bugNum++
        }
    }

    Write-Host ''
    Write-Host '============================' -ForegroundColor Cyan
}

# ===== 清理函数 =====
function Cleanup-ActualFiles {
    # 清理测试目录中的实际输出文件
    Get-ChildItem $TestDir -File -Filter 'actual_T*_output.*' |
        Remove-Item -Force -ErrorAction SilentlyContinue
    
    # 清理 .playwright-cli 目录中的下载文件
    if (Test-Path $PwDir) {
        Get-ChildItem $PwDir -File | Where-Object { $_.Extension -in '.srt','.xlsx' } |
            Remove-Item -Force -ErrorAction SilentlyContinue
    }
}

# ============================================================
#  主流程
# ============================================================

Write-Host ''
Write-Host '============================' -ForegroundColor Cyan
Write-Host ' ScriptGrid Auto Test' -ForegroundColor Cyan
Write-Host '============================' -ForegroundColor Cyan
Write-Host ''

# 1. 检查后端服务
$checkMsg = '检查后端服务 (' + $BaseUrl + ')... '
Write-Host $checkMsg -NoNewline
if (Check-Backend) {
    Write-Host '正常' -ForegroundColor Green
} else {
    Write-Host '失败' -ForegroundColor Red
    Write-Host ''
    Write-Host '错误: 后端服务未运行，请先启动:' -ForegroundColor Red
    Write-Host ('  cd ' + $ProjectDir + ' ; .\ScriptGrid\Scripts\python.exe -m uvicorn app:app --host 0.0.0.0 --port 8000') -ForegroundColor Yellow
    exit 1
}

# 2. 检查 playwright-cli
Write-Host -NoNewline '检查 playwright-cli... '
$pwCheck = Get-Command playwright-cli -ErrorAction SilentlyContinue
if ($pwCheck) {
    Write-Host '正常' -ForegroundColor Green
} else {
    Write-Host '失败' -ForegroundColor Red
    Write-Host ''
    Write-Host '错误: 未找到 playwright-cli，请安装:' -ForegroundColor Red
    Write-Host '  npm install -g @playwright/cli@latest' -ForegroundColor Yellow
    exit 1
}

# 3. 检查 Python 虚拟环境
Write-Host -NoNewline '检查 Python 虚拟环境... '
if (Test-Path $PythonExe) {
    Write-Host '正常' -ForegroundColor Green
} else {
    Write-Host '失败' -ForegroundColor Red
    Write-Host ''
    Write-Host ('错误: 未找到 Python 虚拟环境: ' + $PythonExe) -ForegroundColor Red
    exit 1
}

# 4. 检查 JS 模板
Write-Host -NoNewline '检查 JS 模板... '
$synTemplate = Join-Path $TemplateDir 'sync_test.js'
$asynTemplate = Join-Path $TemplateDir 'async_test.js'
if ((Test-Path $synTemplate) -and (Test-Path $asynTemplate)) {
    Write-Host '正常' -ForegroundColor Green
} else {
    Write-Host '失败' -ForegroundColor Red
    Write-Host ''
    Write-Host '错误: 未在 templates/ 中找到 JS 模板文件' -ForegroundColor Red
    exit 1
}

# 5. 清理旧的实际输出文件
Cleanup-ActualFiles

# 6. 启动浏览器
Write-Host -NoNewline '启动 Edge 浏览器 (无头模式)... '
$openResult = & playwright-cli open --browser=msedge $BaseUrl 2>&1
$openOutput = $openResult | Out-String
if ($LASTEXITCODE -ne 0 -and $openOutput -notmatch 'already') {
    Write-Host '失败' -ForegroundColor Red
    Write-Host ''
    Write-Host '错误: 无法启动浏览器' -ForegroundColor Red
    Write-Host $openOutput
    exit 1
}
Write-Host '正常' -ForegroundColor Green

Start-Sleep -Seconds 2

# 7. 执行测试用例
$totalCount = $TestCases.Count

foreach ($tc in $TestCases) {
    Write-Host ''
    Write-Host ('[' + $tc.Id + '/' + $totalCount + '] ' + $tc.Label) -NoNewline

    if ($tc.Mode -eq 'sync') {
        Run-SyncTest $tc
    } else {
        Run-AsyncTest $tc
    }
}

# 8. 关闭浏览器
Write-Host ''
Write-Host -NoNewline '关闭浏览器... '
$closeResult = & playwright-cli close 2>&1
$closeOutput = $closeResult | Out-String
Write-Host '正常' -ForegroundColor Green

# 9. 清理实际输出文件
Cleanup-ActualFiles

# 10. 打印报告
Print-Report

# 11. 退出码
if ($script:FailCount -gt 0) {
    exit 1
} else {
    exit 0
}
