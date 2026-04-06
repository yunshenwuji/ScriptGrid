"""
OCR 引擎模块
专用于 SUP 字幕的光学字符识别。
"""

import os
import re
import logging
import numpy as np
from PIL import Image
import constants
from exceptions import OcrRecognitionError, OnnxRuntimeError

# 配置日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


class SupOcrEngine:
    """专用于 SUP 字幕的 OCR 识别引擎(使用 TorchfreeEasyOCR)"""
    
    def __init__(self, language_codes=None):
        """
        初始化 OCR 引擎
        :param language_codes: 支持的语言代码列表,默认为中英文
        """
        if language_codes is None:
            language_codes = constants.DEFAULT_OCR_LANGUAGES
        
        # 验证语言代码有效性
        self.language_codes = self._validate_language_codes(language_codes)
        
        # 设置多个可能的模型路径环境变量,确保TorchfreeEasyOCR从/models目录读取模型
        model_dir = os.path.join(os.getcwd(), constants.OCR_MODEL_DIRECTORY)
        os.environ['EASYOCR_MODULE_PATH'] = model_dir
        os.environ['MODULE_PATH'] = model_dir
        
        # 设置用户目录下的.TorchfreeOCR目录也指向我们的models目录
        user_home = os.path.expanduser('~')
        torchfree_ocr_dir = os.path.join(user_home, '.TorchfreeOCR')
        if not os.path.exists(torchfree_ocr_dir) or not os.path.islink(torchfree_ocr_dir):
            try:
                if os.path.exists(torchfree_ocr_dir) and not os.path.islink(torchfree_ocr_dir):
                    import shutil
                    backup_dir = torchfree_ocr_dir + '.backup'
                    if not os.path.exists(backup_dir):
                        shutil.move(torchfree_ocr_dir, backup_dir)
                elif os.path.exists(torchfree_ocr_dir) and os.path.islink(torchfree_ocr_dir):
                    os.unlink(torchfree_ocr_dir)  # 删除现有符号链接
                
                # 创建新的符号链接
                os.symlink(model_dir, torchfree_ocr_dir, target_is_directory=True)
            except (OSError, NotImplementedError, PermissionError) as e:
                pass  # 忽略符号链接创建失败
        
        # 尝试在初始化之前动态修改TorchfreeEasyOCR的模型路径
        try:
            import torchfree_ocr.torchfree_ocr as tfocr_module
            # 设置模块级别的模型路径
            if hasattr(tfocr_module, 'MODULE_PATH'):
                tfocr_module.MODULE_PATH = model_dir
            if hasattr(tfocr_module, 'model_storage_directory'):
                tfocr_module.model_storage_directory = model_dir
        except ImportError:
            pass  # 如果无法导入内部模块,就跳过
        
        try:
            import torchfree_ocr as ocr_module
            # 初始化 TorchfreeEasyOCR 读取器
            # 注意: torchfree_ocr.Reader 只支持 lang_list 和 recognizer 参数
            self.reader = ocr_module.Reader(
                lang_list=self.language_codes,
                recognizer=True  # 启用识别功能
            )
        except ImportError as e:
            raise OcrRecognitionError(f"TorchfreeEasyOCR 模块未安装: {e}") from e
        except Exception as e:
            # 检查是否为 ONNX Runtime 相关错误
            error_msg = str(e).lower()
            if 'onnx' in error_msg or 'onnxruntime' in error_msg:
                raise OnnxRuntimeError(f"ONNX Runtime 初始化失败: {e}") from e
            else:
                raise OcrRecognitionError(f"OCR 引擎初始化失败: {e}") from e
    
    def _validate_language_codes(self, language_codes):
        """
        验证语言代码有效性
        :param language_codes: 语言代码列表
        :return: 验证后的语言代码列表
        """
        valid_languages = set(constants.SUPPORTED_LANGUAGES.keys()) - {'auto'}  # 移除自动检测
        validated_codes = []
        
        for code in language_codes:
            if code in valid_languages:
                validated_codes.append(code)
            else:
                logger.warning(f"不支持的语言代码 '{code}',将被忽略")
        
        # 如果没有有效的语言代码,使用默认语言
        if not validated_codes:
            logger.warning("没有有效的语言代码,使用默认中英文")
            validated_codes = constants.DEFAULT_OCR_LANGUAGES
        
        return validated_codes
    
    def recognize_subtitle_text(self, image_pil):
        """
        识别字幕图像中的文本
        :param image_pil: PIL 图像对象
        :return: 识别出的文本字符串
        """
        try:
            # 图像预处理
            processed_image = self._preprocess_subtitle_image(image_pil)
            
            # 转换为 numpy 数组以供 TorchfreeEasyOCR 使用
            image_array = np.array(processed_image)
            
            # OCR 识别,使用 detail=1 获取详细信息
            results = self.reader.readtext(image_array, detail=1)
            
            # 文本后处理
            return self._postprocess_ocr_results(results)
            
        except Exception as e:
            # OCR 失败时返回空字符串,而非抛出异常
            error_msg = str(e).lower()
            if 'onnx' in error_msg or 'onnxruntime' in error_msg:
                logger.warning(f"ONNX Runtime OCR 识别失败: {e}")
            else:
                logger.warning(f"OCR 识别失败: {e}")
            return ""
    
    def _preprocess_subtitle_image(self, image):
        """
        字幕图像预处理,提高 OCR 准确率
        """
        try:
            # 转换为 RGB模式(如果是 RGBA)
            if image.mode == 'RGBA':
                # 使用白色背景合并透明通道
                white_background = Image.new('RGB', image.size, (255, 255, 255))
                white_background.paste(image, mask=image.split()[-1])  # 使用 alpha 通道作为 mask
                image = white_background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 尺寸标准化:如果图像太小,放大以提高识别准确率
            width, height = image.size
            if width < 200 or height < 50:
                scale_factor = max(200 // width, 50 // height, 2)
                new_size = (width * scale_factor, height * scale_factor)
                image = image.resize(new_size, Image.LANCZOS)
            
            return image
            
        except Exception as e:
            logger.warning(f"图像预处理失败: {e}")
            return image  # 返回原图像
    
    def _postprocess_ocr_results(self, results):
        """
        OCR 结果后处理
        :param results: EasyOCR 返回的结果列表
        :return: 清理后的文本字符串
        """
        if not results:
            return ""
        
        # 提取所有识别的文本,按置信度排序
        texts = []
        for (bbox, text, confidence) in results:
            # 过滤低置信度的结果
            if confidence > 0.5:  # 调整阈值根据实际效果
                texts.append(text.strip())
        
        # 合并为一行文本
        combined_text = ' '.join(texts).strip()
        
        # 清理多余的空格
        combined_text = re.sub(r'\s+', ' ', combined_text)
        
        return combined_text
