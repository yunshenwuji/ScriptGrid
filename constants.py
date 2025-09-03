"""
常量定义模块
用于存储项目中使用的各种常量，便于统一管理和维护。
"""

# --- GUI 相关 ---
WINDOW_TITLE = "述格 (ScriptGrid)"
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 350

BUTTON_WIDTH = 30
BUTTON_HEIGHT = 2
BUTTON_PADY = 10

BUTTON_TEXT_CONVERT_TO_EXCEL = "字幕转表格 (.ass, .srt -> .xlsx)"
BUTTON_TEXT_ASS_TO_SRT = "ASS 转 SRT (.ass -> .srt)"
BUTTON_TEXT_XLSX_TO_SRT = "表格转字幕 (.xlsx -> .srt)"
BUTTON_TEXT_CLOSE = "关闭软件"

# --- 文件对话框相关 ---
DIALOG_TITLE_SELECT_SUBTITLE = "请选择字幕文件"
DIALOG_TITLE_SELECT_ASS = "请选择 ASS 字幕文件"
DIALOG_TITLE_SELECT_XLSX = "请选择字幕表格文件"

FILETYPE_SUBTITLE = ("字幕文件", "*.ass *.srt")
FILETYPE_ASS = ("ASS 字幕文件", "*.ass")
FILETYPE_XLSX = ("Excel 文件", "*.xlsx")
FILETYPE_ALL = ("所有文件", "*.*")

# --- Excel 表头 ---
EXCEL_HEADERS = ["序号", "开始时间", "结束时间", "字幕内容"]
EXCEL_SHEET_NAME = "Sheet1"

# --- SRT 格式相关 ---
# SRT块由序号、时间码、文本和一个空行组成

# --- 错误与提示信息 ---
MSG_WARNING_UNSUPPORTED_FORMAT = "格式不支持"
MSG_WARNING_NO_DATA_PARSED = "解析失败"
MSG_WARNING_NO_DATA_PARSED_DETAIL_SUBTITLE = "未能从文件中提取任何有效的字幕数据。"
MSG_WARNING_NO_DATA_PARSED_DETAIL_ASS = "未能从 ASS 文件中提取任何有效的字幕数据。"
MSG_WARNING_NO_DATA_PARSED_DETAIL_XLSX = "未能从 Excel 文件中提取任何有效的字幕数据。请检查文件格式和表头。"
MSG_WARNING_INCORRECT_HEADER = "Excel 文件表头不正确。期望: {expected}, 实际: {actual}"

MSG_ERROR_PROCESSING = "发生错误"
MSG_ERROR_PROCESSING_DETAIL_SUBTITLE = "处理文件时发生错误: \n{error}"
MSG_ERROR_PROCESSING_DETAIL_ASS = "处理 ASS 文件时发生错误: \n{error}"
MSG_ERROR_PROCESSING_DETAIL_XLSX = "处理 Excel 文件时发生错误: \n{error}"
MSG_ERROR_PARSING_XLSX = "解析 Excel 文件时出错: {error}"
MSG_ERROR_WRITING_SRT = "写入 SRT 文件时出错: {error}"

# --- SUP PGS 转换相关 ---
BUTTON_TEXT_SUP_TO_SRT = "SUP 转 SRT (.sup -> .srt)"
BUTTON_TEXT_SUP_TO_EXCEL = "SUP 转表格 (.sup -> .xlsx)"

DIALOG_TITLE_SELECT_SUP = "请选择 SUP 字幕文件"
FILETYPE_SUP = ("SUP 字幕文件", "*.sup")

MSG_WARNING_NO_DATA_PARSED_DETAIL_SUP = "未能从 SUP 文件中提取任何有效的字幕数据。"
MSG_ERROR_PROCESSING_DETAIL_SUP = "处理 SUP 文件时发生错误: \n{error}"
MSG_ERROR_PARSING_SUP = "解析 SUP 文件时出错: {error}"
MSG_ERROR_OCR_RECOGNITION = "OCR 识别错误: {error}"
MSG_ERROR_LANGUAGE_DETECTION = "语言检测失败: {error}"
MSG_INFO_SUCCESS_DETAIL_SUP_TO_SRT = "SUP 转 SRT 完成！\n文件已保存至:\n{path}"
MSG_INFO_SUCCESS_DETAIL_SUP_TO_EXCEL = "SUP 转表格完成！\n文件已保存至:\n{path}"
MSG_INFO_OCR_PROCESSING = "OCR识别中，请耐心等待..."

# OCR 相关常量
DEFAULT_OCR_LANGUAGES = ['ch_sim', 'en']  # 默认支持中英文
OCR_MODEL_DIRECTORY = "models"  # EasyOCR 模型存储目录
OCR_BATCH_SIZE = 10  # OCR 批处理大小

MSG_INFO_SUCCESS = "成功"
MSG_INFO_SUCCESS_DETAIL_TO_EXCEL = "转换完成！\n文件已保存至:\n{path}"
MSG_INFO_SUCCESS_DETAIL_ASS_TO_SRT = "ASS 转 SRT 完成！\n文件已保存至:\n{path}"
MSG_INFO_SUCCESS_DETAIL_XLSX_TO_SRT = "表格转字幕完成！\n文件已保存至:\n{path}"

# EasyOCR 支持的语言映射（语言代码 -> 显示名称）
SUPPORTED_LANGUAGES = {
    'auto': '自动检测',
    'ch_sim': '简体中文',
    'ch_tra': '繁体中文',
    'en': '英语',
    'ja': '日语',
    'ko': '韩语',
    'th': '泰语',
    'vi': '越南语',
    'ar': '阿拉伯语',
    'de': '德语',
    'fr': '法语',
    'ru': '俄语',
    'es': '西班牙语',
    'pt': '葡萄牙语',
    'it': '意大利语',
    'nl': '荷兰语',
    'pl': '波兰语',
    'tr': '土耳其语',
    'hi': '印地语',
    'bn': '孟加拉语'
}

# EasyOCR 支持的语言映射（英文版）
SUPPORTED_LANGUAGES_EN = {
    'auto': 'Auto Detect',
    'ch_sim': 'Simplified Chinese',
    'ch_tra': 'Traditional Chinese',
    'en': 'English',
    'ja': 'Japanese',
    'ko': 'Korean',
    'th': 'Thai',
    'vi': 'Vietnamese',
    'ar': 'Arabic',
    'de': 'German',
    'fr': 'French',
    'ru': 'Russian',
    'es': 'Spanish',
    'pt': 'Portuguese',
    'it': 'Italian',
    'nl': 'Dutch',
    'pl': 'Polish',
    'tr': 'Turkish',
    'hi': 'Hindi',
    'bn': 'Bengali'
}