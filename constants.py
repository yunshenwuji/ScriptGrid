"""
常量定义模块
用于存储项目中使用的各种常量，便于统一管理和维护。
"""

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

MSG_INFO_SUCCESS = "成功"
MSG_INFO_SUCCESS_DETAIL_TO_EXCEL = "转换完成！\n文件已保存至:\n{path}"
MSG_INFO_SUCCESS_DETAIL_ASS_TO_SRT = "ASS 转 SRT 完成！\n文件已保存至:\n{path}"
MSG_INFO_SUCCESS_DETAIL_XLSX_TO_SRT = "表格转字幕完成！\n文件已保存至:\n{path}"

# EasyOCR 支持的语言映射（语言代码 -> 显示名称）
# 基于 TorchfreeEasyOCR 支持的语言，与预置 ONNX 模型对应
SUPPORTED_LANGUAGES = {
    'auto': '自动检测',
    'ch_sim': '简体中文',
    'ch_tra': '繁体中文', 
    'en': '英语',
    'ja': '日语',
    'ko': '韩语',
    'th': '泰语',
    'ar': '阿拉伯语',
    'hi': '印地语',
    'bn': '孟加拉语',
    'ta': '泰米尔语',
    'te': '泰卢固语',
    'kn': '卡纳达语',
    'de': '德语',
    'fr': '法语',
    'ru': '俄语',
    'cyrillic': '西里尔字母'
}

# EasyOCR 支持的语言映射（英文版）
# 基于 TorchfreeEasyOCR 支持的语言，与预置 ONNX 模型对应
SUPPORTED_LANGUAGES_EN = {
    'auto': 'Auto Detect',
    'ch_sim': 'Simplified Chinese',
    'ch_tra': 'Traditional Chinese',
    'en': 'English',
    'ja': 'Japanese',
    'ko': 'Korean',
    'th': 'Thai',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'bn': 'Bengali',
    'ta': 'Tamil',
    'te': 'Telugu',
    'kn': 'Kannada',
    'de': 'German',
    'fr': 'French',
    'ru': 'Russian',
    'cyrillic': 'Cyrillic'
}