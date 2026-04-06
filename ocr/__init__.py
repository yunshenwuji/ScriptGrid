"""
OCR 光学字符识别模块
用于 SUP 字幕图像的文字识别和语言检测。
"""

from ocr.engine import SupOcrEngine
from ocr.language_detector import detect_subtitle_language

__all__ = ['SupOcrEngine', 'detect_subtitle_language']
