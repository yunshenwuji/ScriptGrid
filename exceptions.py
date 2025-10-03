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

# SUP PGS 相关异常类
class SupParseError(ParseError):
    """SUP文件解析错误"""
    pass

class OcrRecognitionError(ParseError):
    """OCR识别错误（支持 PyTorch 和 ONNX Runtime）"""
    pass

class LanguageDetectionError(ParseError):
    """语言检测错误"""
    pass

class OnnxRuntimeError(OcrRecognitionError):
    """ONNX Runtime 相关错误"""
    pass