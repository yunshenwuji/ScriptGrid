#!/usr/bin/env bash
# ============================================================
# ScriptGrid 前端自动化测试脚本 (Linux 版)
# 基于 playwright-cli + Chromium 浏览器（无头模式）
# 与 run_test.ps1 功能等价，路径自动推导
# ============================================================

set -u
# 不使用 set -e：测试失败时仍需继续后续用例

# ===== 配置区 =====
BASE_URL='http://127.0.0.1:8000'
# 自动根据脚本所在位置推导路径，确保任意 Linux 开发机克隆即用
# 约定脚本位于 <项目根>/test/run_test.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$SCRIPT_DIR"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PYTHON_EXE="$PROJECT_DIR/ScriptGrid/bin/python"
PW_DIR="$TEST_DIR/.playwright-cli"
TEMPLATE_DIR="$TEST_DIR/templates"

# ===== 颜色定义 =====
C_RESET=$'\033[0m'
C_RED=$'\033[31m'
C_GREEN=$'\033[32m'
C_YELLOW=$'\033[33m'
C_CYAN=$'\033[36m'

# ===== 测试用例 =====
# 字段顺序: ID|Input|Type|Expected|Mode|Label
TEST_CASES=(
    "T01|ass/input.ass|ass_to_srt|ass/output.srt|sync|ASS-SRT"
    "T02|ass/input.ass|subtitle_to_excel|ass/output.xlsx|sync|ASS-Excel"
    "T03|ass/input.ass|auto_narration_timing|ass/narration_output.srt|sync|ASS-Narration"
    "T04|srt/input.srt|subtitle_to_excel|srt/output.xlsx|sync|SRT-Excel"
    "T05|srt/input.srt|auto_narration_timing|srt/narration_output.srt|sync|SRT-Narration"
    "T06|xlsx/input.xlsx|xlsx_to_srt|xlsx/output.srt|sync|XLSX-SRT"
    "T07|sup/input.sup|sup_to_srt|sup/input.srt|async|SUP-SRT"
    "T08|sup/input.sup|sup_to_excel|sup/input.xlsx|async|SUP-Excel"
    "T09|sup/input.sup|auto_narration_timing|sup/narration_input.srt|async|SUP-Narration"
)

# ===== 结果存储（平行数组） =====
PASS_COUNT=0
FAIL_COUNT=0
RESULT_IDS=()
RESULT_LABELS=()
RESULT_STATUSES=()
RESULT_DETAILS=()

# ===== 加载 JS 模板 =====
SYNC_JS_TEMPLATE="$(cat "$TEMPLATE_DIR/sync_test.js" 2>/dev/null || true)"
ASYNC_JS_TEMPLATE="$(cat "$TEMPLATE_DIR/async_test.js" 2>/dev/null || true)"

# ===== 辅助函数 =====
check_backend() {
    curl -sSf -m 5 "$BASE_URL" -o /dev/null
}

run_playwright_code() {
    local code="$1"
    playwright-cli run-code "$code" 2>&1
}

get_actual_file_path() {
    local test_id="$1"
    local expected_path="$2"
    local ext="${expected_path##*.}"
    echo "$TEST_DIR/actual_${test_id}_output.${ext}"
}

build_js_code() {
    # 模板占位符替换；Linux 路径天然使用 /，不需要额外转换
    local template="$1"
    local input_path="$2"
    local conv_type="$3"
    local output_path="$4"
    local code="$template"
    code="${code//\{\{INPUT_PATH\}\}/$input_path}"
    code="${code//\{\{CONV_TYPE\}\}/$conv_type}"
    code="${code//\{\{OUTPUT_PATH\}\}/$output_path}"
    echo "$code"
}

compare_test_output() {
    # 输出格式: "0|" 表示通过, "1|<detail>" 表示失败
    local actual_path="$1"
    local expected_path="$2"
    if [[ ! -f "$actual_path" ]]; then
        echo "1|Actual file not found: $actual_path"
        return
    fi
    if [[ ! -f "$expected_path" ]]; then
        echo "1|Expected file not found: $expected_path"
        return
    fi
    local compare_script="$TEST_DIR/compare.py"
    local compare_output exit_code
    compare_output="$("$PYTHON_EXE" "$compare_script" "$actual_path" "$expected_path" --quiet 2>&1)"
    exit_code=$?
    if [[ $exit_code -eq 0 ]] && echo "$compare_output" | grep -q '^PASS|'; then
        echo "0|"
    else
        local detail
        if echo "$compare_output" | grep -q '^FAIL|'; then
            detail="$(echo "$compare_output" | sed -n 's/^FAIL|//p' | head -1)"
        else
            detail="$(echo "$compare_output" | tr -d '\r' | head -3 | tr '\n' ';')"
        fi
        if [[ -z "${detail// }" ]]; then
            detail="未知对比错误"
        fi
        echo "1|$detail"
    fi
}

add_result() {
    RESULT_IDS+=("$1")
    RESULT_LABELS+=("$2")
    RESULT_STATUSES+=("$3")
    RESULT_DETAILS+=("$4")
}

# ===== 同步测试函数 =====
run_sync_test() {
    local id="$1" input="$2" conv_type="$3" expected="$4" label="$5"
    local input_path="$TEST_DIR/$input"
    local expected_path="$TEST_DIR/$expected"
    local actual_path
    actual_path="$(get_actual_file_path "$id" "$expected_path")"

    printf ' ...'

    local js_code
    js_code="$(build_js_code "$SYNC_JS_TEMPLATE" "$input_path" "$conv_type" "$actual_path")"

    local output
    output="$(run_playwright_code "$js_code")"

    # 检测真正的 JavaScript 错误
    if echo "$output" | grep -qE '^### Error|SyntaxError:|TypeError:|ReferenceError:'; then
        printf ' %s失败%s\n\n' "$C_RED" "$C_RESET"
        FAIL_COUNT=$((FAIL_COUNT+1))
        local detail
        detail="$(echo "$output" | head -c 200 | tr '\n' ' ')"
        add_result "$id" "$label" "FAIL" "转换失败: $detail"
        return
    fi

    # 检测超时
    if echo "$output" | grep -qE '^[[:space:]]*TIMEOUT[[:space:]]*$|TimeoutError'; then
        printf ' %s失败 (超时)%s\n\n' "$C_RED" "$C_RESET"
        FAIL_COUNT=$((FAIL_COUNT+1))
        add_result "$id" "$label" "FAIL" "转换超时"
        return
    fi

    if [[ ! -f "$actual_path" ]]; then
        printf ' %s失败 (未找到下载文件)%s\n\n' "$C_RED" "$C_RESET"
        FAIL_COUNT=$((FAIL_COUNT+1))
        add_result "$id" "$label" "FAIL" "下载文件未保存: $actual_path"
        return
    fi

    printf ' 对比中...'

    local cmp cmp_status cmp_detail
    cmp="$(compare_test_output "$actual_path" "$expected_path")"
    cmp_status="${cmp%%|*}"
    cmp_detail="${cmp#*|}"
    if [[ "$cmp_status" == "0" ]]; then
        printf ' %s通过%s\n' "$C_GREEN" "$C_RESET"
        PASS_COUNT=$((PASS_COUNT+1))
        add_result "$id" "$label" "PASS" ""
    else
        printf ' %s失败%s\n' "$C_RED" "$C_RESET"
        FAIL_COUNT=$((FAIL_COUNT+1))
        add_result "$id" "$label" "FAIL" "$cmp_detail"
    fi
}

# ===== 异步 SUP 测试函数 =====
run_async_test() {
    local id="$1" input="$2" conv_type="$3" expected="$4" label="$5"
    local input_path="$TEST_DIR/$input"
    local expected_path="$TEST_DIR/$expected"
    local actual_path
    actual_path="$(get_actual_file_path "$id" "$expected_path")"

    printf ' ... (异步，最长 10 分钟)'

    local test_start_time
    test_start_time=$(date +%s)

    # 清理 .playwright-cli/ 中的旧下载文件
    if [[ -d "$PW_DIR" ]]; then
        find "$PW_DIR" -maxdepth 1 -type f \( -name '*.srt' -o -name '*.xlsx' \) -delete 2>/dev/null
    fi

    local js_code
    js_code="$(build_js_code "$ASYNC_JS_TEMPLATE" "$input_path" "$conv_type" "")"

    local output
    output="$(run_playwright_code "$js_code")"

    # 提取 ### Result 段中第一行（去掉两端的双引号）
    local result_value=""
    if echo "$output" | grep -q '^### Result'; then
        result_value="$(echo "$output" | awk '/^### Result/{flag=1;next} /^###/{flag=0} flag' | head -1 | sed -n 's/^"\(.*\)"$/\1/p')"
    fi

    # 检查 Result 中的错误
    if echo "$output" | grep -q 'ERROR:' && [[ "$result_value" == ERROR:* ]]; then
        local err_msg="${result_value#ERROR:}"
        err_msg="${err_msg# }"
        printf ' %s失败: %s%s\n\n' "$C_RED" "$err_msg" "$C_RESET"
        FAIL_COUNT=$((FAIL_COUNT+1))
        add_result "$id" "$label" "FAIL" "转换错误: $err_msg"
        return
    fi

    # 检查 Result 中的超时
    if [[ "$result_value" == "TIMEOUT" ]]; then
        printf ' %s失败 (超时 10分钟)%s\n\n' "$C_RED" "$C_RESET"
        FAIL_COUNT=$((FAIL_COUNT+1))
        add_result "$id" "$label" "FAIL" "转换超时"
        return
    fi

    # 提取耗时
    local elapsed=""
    if [[ "$result_value" =~ ^SUCCESS:([0-9]+s) ]]; then
        elapsed=" (${BASH_REMATCH[1]})"
    fi

    printf ' 完成%s 对比中...' "$elapsed"

    # 在 .playwright-cli/ 中查找下载的文件
    local ext="${expected_path##*.}"
    local downloaded_file=""
    local wait_count=0
    while [[ $wait_count -lt 30 ]]; do
        sleep 1
        downloaded_file="$(find "$PW_DIR" -maxdepth 1 -type f -name "*.${ext}" -newermt "@$test_start_time" 2>/dev/null | head -1)"
        if [[ -n "$downloaded_file" ]]; then break; fi
        wait_count=$((wait_count+1))
    done

    if [[ -z "$downloaded_file" ]]; then
        printf ' %s失败 (未找到下载文件)%s\n\n' "$C_RED" "$C_RESET"
        FAIL_COUNT=$((FAIL_COUNT+1))
        add_result "$id" "$label" "FAIL" "未在 $PW_DIR 中找到下载文件"
        return
    fi

    cp -f "$downloaded_file" "$actual_path"

    local cmp cmp_status cmp_detail
    cmp="$(compare_test_output "$actual_path" "$expected_path")"
    cmp_status="${cmp%%|*}"
    cmp_detail="${cmp#*|}"
    if [[ "$cmp_status" == "0" ]]; then
        printf ' %s通过%s\n' "$C_GREEN" "$C_RESET"
        PASS_COUNT=$((PASS_COUNT+1))
        add_result "$id" "$label" "PASS" ""
    else
        printf ' %s失败%s\n' "$C_RED" "$C_RESET"
        FAIL_COUNT=$((FAIL_COUNT+1))
        add_result "$id" "$label" "FAIL" "$cmp_detail"
    fi
}

# ===== 打印测试报告 =====
print_report() {
    echo ""
    printf '%s============================%s\n' "$C_CYAN" "$C_RESET"
    printf '%s ScriptGrid 测试报告%s\n' "$C_CYAN" "$C_RESET"
    printf '%s============================%s\n' "$C_CYAN" "$C_RESET"
    echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "总计: ${#TEST_CASES[@]}"
    printf '%s通过: %d%s  %s失败: %d%s\n' "$C_GREEN" "$PASS_COUNT" "$C_RESET" "$C_RED" "$FAIL_COUNT" "$C_RESET"
    echo ""
    echo "详细信息:"

    local i
    for i in "${!RESULT_IDS[@]}"; do
        local id="${RESULT_IDS[$i]}"
        local label="${RESULT_LABELS[$i]}"
        local status="${RESULT_STATUSES[$i]}"
        local detail="${RESULT_DETAILS[$i]}"
        local icon status_text
        if [[ "$status" == "PASS" ]]; then
            icon="✅"
            status_text="通过"
        else
            icon="❌"
            status_text="失败"
        fi
        printf '  %-22s %s %s' "${id} ${label}" "$icon" "$status_text"
        if [[ "$status" == "FAIL" && -n "${detail// }" ]]; then
            local short="${detail:0:100}"
            printf ' %s(%s)%s\n' "$C_YELLOW" "$short" "$C_RESET"
        else
            echo ""
        fi
    done

    # BUG 列表
    local has_fail=0
    local s
    for s in "${RESULT_STATUSES[@]}"; do
        if [[ "$s" == "FAIL" ]]; then has_fail=1; break; fi
    done

    if [[ $has_fail -eq 1 ]]; then
        echo ""
        printf '%sBUG 列表:%s\n' "$C_RED" "$C_RESET"
        local bug_num=1
        for i in "${!RESULT_IDS[@]}"; do
            if [[ "${RESULT_STATUSES[$i]}" != "FAIL" ]]; then continue; fi
            local id="${RESULT_IDS[$i]}"
            local label="${RESULT_LABELS[$i]}"
            local detail="${RESULT_DETAILS[$i]}"
            printf '%s  BUG-%03d: [%s] %s%s\n' "$C_RED" "$bug_num" "$id" "$label" "$C_RESET"
            if [[ -n "${detail// }" ]]; then
                IFS=';' read -ra parts <<< "$detail"
                local count=0
                local part
                for part in "${parts[@]}"; do
                    [[ $count -ge 3 ]] && break
                    part="${part#"${part%%[![:space:]]*}"}"
                    part="${part%"${part##*[![:space:]]}"}"
                    [[ -z "$part" ]] && continue
                    printf '    - %s%s%s\n' "$C_YELLOW" "$part" "$C_RESET"
                    count=$((count+1))
                done
            fi
            bug_num=$((bug_num+1))
        done
    fi

    echo ""
    printf '%s============================%s\n' "$C_CYAN" "$C_RESET"
}

# ===== 清理函数 =====
cleanup_actual_files() {
    find "$TEST_DIR" -maxdepth 1 -type f -name 'actual_T*_output.*' -delete 2>/dev/null
    if [[ -d "$PW_DIR" ]]; then
        find "$PW_DIR" -maxdepth 1 -type f \( -name '*.srt' -o -name '*.xlsx' \) -delete 2>/dev/null
    fi
}

# ============================================================
#  主流程
# ============================================================

echo ""
printf '%s============================%s\n' "$C_CYAN" "$C_RESET"
printf '%s ScriptGrid Auto Test%s\n' "$C_CYAN" "$C_RESET"
printf '%s============================%s\n' "$C_CYAN" "$C_RESET"
echo ""

# 1. 检查后端服务
printf '检查后端服务 (%s)... ' "$BASE_URL"
if check_backend; then
    printf '%s正常%s\n' "$C_GREEN" "$C_RESET"
else
    printf '%s失败%s\n\n' "$C_RED" "$C_RESET"
    printf '%s错误: 后端服务未运行，请先启动:%s\n' "$C_RED" "$C_RESET"
    printf '%s  cd %s && ./ScriptGrid/bin/python -m uvicorn app:app --host 0.0.0.0 --port 8000%s\n' "$C_YELLOW" "$PROJECT_DIR" "$C_RESET"
    exit 1
fi

# 2. 检查 playwright-cli
printf '检查 playwright-cli... '
if command -v playwright-cli >/dev/null 2>&1; then
    printf '%s正常%s\n' "$C_GREEN" "$C_RESET"
else
    printf '%s失败%s\n\n' "$C_RED" "$C_RESET"
    printf '%s错误: 未找到 playwright-cli，请安装:%s\n' "$C_RED" "$C_RESET"
    printf '%s  npm install -g @playwright/cli@latest%s\n' "$C_YELLOW" "$C_RESET"
    exit 1
fi

# 3. 检查 Python 虚拟环境
printf '检查 Python 虚拟环境... '
if [[ -x "$PYTHON_EXE" ]]; then
    printf '%s正常%s\n' "$C_GREEN" "$C_RESET"
else
    printf '%s失败%s\n\n' "$C_RED" "$C_RESET"
    printf '%s错误: 未找到 Python 虚拟环境: %s%s\n' "$C_RED" "$PYTHON_EXE" "$C_RESET"
    exit 1
fi

# 4. 检查 JS 模板
printf '检查 JS 模板... '
if [[ -f "$TEMPLATE_DIR/sync_test.js" && -f "$TEMPLATE_DIR/async_test.js" ]]; then
    printf '%s正常%s\n' "$C_GREEN" "$C_RESET"
else
    printf '%s失败%s\n\n' "$C_RED" "$C_RESET"
    printf '%s错误: 未在 templates/ 中找到 JS 模板文件%s\n' "$C_RED" "$C_RESET"
    exit 1
fi

# 5. 清理旧的实际输出文件
cleanup_actual_files

# 5.1 启动浏览器前：若 .playwright-cli 目录不为空则整体清空
#     避免历史下载文件或残留日志影响本轮异步用例的下载文件识别
printf '检查 .playwright-cli 目录... '
if [[ -d "$PW_DIR" ]]; then
    item_count=$(find "$PW_DIR" -mindepth 1 -maxdepth 1 2>/dev/null | wc -l)
    if [[ $item_count -gt 0 ]]; then
        find "$PW_DIR" -mindepth 1 -delete 2>/dev/null
        printf '%s已清空 (%d 项)%s\n' "$C_GREEN" "$item_count" "$C_RESET"
    else
        printf '%s已为空%s\n' "$C_GREEN" "$C_RESET"
    fi
else
    printf '%s不存在，跳过%s\n' "$C_YELLOW" "$C_RESET"
fi

# 6. 启动浏览器（Linux 默认使用 chromium）
printf '启动 Chromium 浏览器 (无头模式)... '
open_output="$(playwright-cli open --browser=chromium "$BASE_URL" 2>&1)"
open_status=$?
if [[ $open_status -ne 0 ]] && ! echo "$open_output" | grep -qi 'already'; then
    printf '%s失败%s\n\n' "$C_RED" "$C_RESET"
    printf '%s错误: 无法启动浏览器%s\n' "$C_RED" "$C_RESET"
    echo "$open_output"
    exit 1
fi
printf '%s正常%s\n' "$C_GREEN" "$C_RESET"

sleep 2

# 7. 执行测试用例
total_count=${#TEST_CASES[@]}
for tc in "${TEST_CASES[@]}"; do
    IFS='|' read -r id input conv_type expected mode label <<< "$tc"
    echo ""
    printf '[%s/%d] %s' "$id" "$total_count" "$label"
    if [[ "$mode" == "sync" ]]; then
        run_sync_test "$id" "$input" "$conv_type" "$expected" "$label"
    else
        run_async_test "$id" "$input" "$conv_type" "$expected" "$label"
    fi
done

# 8. 关闭浏览器
echo ""
printf '关闭浏览器... '
playwright-cli close >/dev/null 2>&1
printf '%s正常%s\n' "$C_GREEN" "$C_RESET"

# 9. 清理实际输出文件
cleanup_actual_files

# 10. 打印报告
print_report

# 11. 退出码
if [[ $FAIL_COUNT -gt 0 ]]; then
    exit 1
else
    exit 0
fi
