"""
语言检测模块
自动检测 SUP 字幕的语言类型。
"""

import os
import re
import logging
from ocr.engine import SupOcrEngine
import constants

# 配置日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def detect_subtitle_language(sample_images, max_samples=20):
    """
    自动检测字幕语言(使用 TorchfreeEasyOCR)
    :param sample_images: 样本图像列表
    :param max_samples: 最大样本数量(默认20帧)
    :return: 检测到的语言代码列表
    """
    try:
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
            except (OSError, NotImplementedError, PermissionError):
                pass  # 忽略符号链接创建失败
        
        # 尝试在初始化之前动态修改TorchfreeEasyOCR的模型路径
        try:
            import torchfree_ocr.torchfree_ocr as tfocr_module
            if hasattr(tfocr_module, 'MODULE_PATH'):
                tfocr_module.MODULE_PATH = model_dir
            if hasattr(tfocr_module, 'model_storage_directory'):
                tfocr_module.model_storage_directory = model_dir
        except ImportError:
            pass  # 如果无法导入内部模块,就跳过
        
        # 使用默认语言进行初步检测(中英文)
        detector = SupOcrEngine(['ch_sim', 'en'])
        
        chinese_count = 0
        english_count = 0
        total_processed = 0
        
        # 对前20帧进行语言检测
        for i, image in enumerate(sample_images[:max_samples]):
            if image is None:
                continue
                
            text = detector.recognize_subtitle_text(image)
            if not text:
                continue
            
            total_processed += 1
            logger.info(f"语言检测样本 {i+1}: {text[:30]}...")
            
            # 简单的字符集检测
            chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
            english_chars = len(re.findall(r'[a-zA-Z]', text))
            
            if chinese_chars > 0:
                chinese_count += 1
            if english_chars > 0:
                english_count += 1
        
        logger.info(f"语言检测结果: 中文={chinese_count}, 英文={english_count}, 总处理样本={total_processed}")
        
        # 根据检测结果决定语言
        if chinese_count > 0 and english_count > 0:
            return ['ch_sim', 'en']  # 中英混合
        elif chinese_count > 0:
            return ['ch_sim']  # 主要为中文
        elif english_count > 0:
            return ['en']  # 主要为英文
        else:
            return constants.DEFAULT_OCR_LANGUAGES  # 默认中英文
            
    except Exception as e:
        logger.warning(f"语言检测失败: {e},使用默认语言")
        return constants.DEFAULT_OCR_LANGUAGES
