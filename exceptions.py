"""
自定义异常类模块
用于定义项目中特定的异常，以便更精确地处理错误。
"""

class SubtitleConverterError(Exception):
    """字幕转换器基础异常类"""
    pass

class ParseError(SubtitleConverterError):
    """解析文件时发生的错误"""
    pass

class WriteError(SubtitleConverterError):
    """写入文件时发生的错误"""
    pass

class ConversionError(SubtitleConverterError):
    """转换过程中发生的通用错误"""
    pass