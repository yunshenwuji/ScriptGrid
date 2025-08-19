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

MSG_INFO_SUCCESS = "成功"
MSG_INFO_SUCCESS_DETAIL_TO_EXCEL = "转换完成！\n文件已保存至:\n{path}"
MSG_INFO_SUCCESS_DETAIL_ASS_TO_SRT = "ASS 转 SRT 完成！\n文件已保存至:\n{path}"
MSG_INFO_SUCCESS_DETAIL_XLSX_TO_SRT = "表格转字幕完成！\n文件已保存至:\n{path}"