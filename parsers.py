"""
字幕解析模块
负责将 .srt, .ass 和 .sup 格式的字幕文件解析为统一的内部数据结构。
内部数据结构: List[List[str]]，每个子列表代表一行字幕，格式为 [index, start_time, end_time, text]。
"""

import os
import re
from exceptions import ParseError, SupParseError, OcrRecognitionError, LanguageDetectionError, OnnxRuntimeError

# SUP PGS 相关导入
try:
    import torchfree_ocr as ocr_module
    import numpy as np
    from PIL import Image
    from pgsreader import PGSReader
    from imagemaker import make_image
    import constants
except ImportError as e:
    print(f"警告: SUP 支持需要额外依赖，请安装: pip install torchfree_ocr onnxruntime")
    print(f"导入错误: {e}")

def parse_srt(file_path):
    """
    解析 .srt 字幕文件。
    :param file_path: .srt 文件的路径。
    :return: 一个二维列表，每个子列表代表一行字幕：[序号, 开始时间, 结束时间, 字幕内容]。
    :raises ParseError: 当解析过程出错时。
    """
    try:
        # 使用 'utf-8-sig' 编码读取文件，可以正确处理可能存在的BOM头
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        # 定义一个强大的正则表达式来匹配一个完整的SRT字幕块
        # re.DOTALL 标志让 '.' 可以匹配包括换行符在内的任意字符
        pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\n(.*?)\n\n', re.DOTALL)
        # 找到所有匹配项
        matches = pattern.findall(content)

        data = [] # 准备存放结果
        for match in matches:
            # match 是一个元组，包含了正则表达式中每个括号捕获到的内容
            index = match[0]
            start_time = match[1]
            end_time = match[2]
            # 将可能存在的多行字幕文本合并为一行，用空格分隔
            text = ' '.join(match[3].replace('\r\n', '\n').split('\n'))
            data.append([index, start_time, end_time, text])

        return data
    except Exception as e:
        raise ParseError(f"解析 SRT 文件 '{file_path}' 时出错: {e}") from e


# ====== SUP PGS 支持 ======

class SupOcrEngine:
    """专用于 SUP 字幕的 OCR 识别引擎（使用 TorchfreeEasyOCR）"""
    
    def __init__(self, language_codes=None):
        """
        初始化 OCR 引擎
        :param language_codes: 支持的语言代码列表，默认为中英文
        """
        if language_codes is None:
            language_codes = constants.DEFAULT_OCR_LANGUAGES
        
        # 验证语言代码有效性
        self.language_codes = self._validate_language_codes(language_codes)
        
        try:
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
                print(f"警告: 不支持的语言代码 '{code}'，将被忽略")
        
        # 如果没有有效的语言代码，使用默认语言
        if not validated_codes:
            print("警告: 没有有效的语言代码，使用默认中英文")
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
            
            # OCR 识别，使用 detail=1 获取详细信息
            results = self.reader.readtext(image_array, detail=1)
            
            # 文本后处理
            return self._postprocess_ocr_results(results)
            
        except Exception as e:
            # OCR 失败时返回空字符串，而非抛出异常
            error_msg = str(e).lower()
            if 'onnx' in error_msg or 'onnxruntime' in error_msg:
                print(f"警告: ONNX Runtime OCR 识别失败: {e}")
            else:
                print(f"警告: OCR 识别失败: {e}")
            return ""
    
    def _preprocess_subtitle_image(self, image):
        """
        字幕图像预处理，提高 OCR 准确率
        """
        try:
            # 转换为 RGB模式（如果是 RGBA）
            if image.mode == 'RGBA':
                # 使用白色背景合并透明通道
                white_background = Image.new('RGB', image.size, (255, 255, 255))
                white_background.paste(image, mask=image.split()[-1])  # 使用 alpha 通道作为 mask
                image = white_background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 尺寸标准化：如果图像太小，放大以提高识别准确率
            width, height = image.size
            if width < 200 or height < 50:
                scale_factor = max(200 // width, 50 // height, 2)
                new_size = (width * scale_factor, height * scale_factor)
                image = image.resize(new_size, Image.LANCZOS)
            
            return image
            
        except Exception as e:
            print(f"警告: 图像预处理失败: {e}")
            return image  # 返回原图像
    
    def _postprocess_ocr_results(self, results):
        """
        OCR 结果后处理
        :param results: EasyOCR 返回的结果列表
        :return: 清理后的文本字符串
        """
        if not results:
            return ""
        
        # 提取所有识别的文本，按置信度排序
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


def _detect_subtitle_language(sample_images, max_samples=20):
    """
    自动棄测字幕语言（使用 TorchfreeEasyOCR）
    :param sample_images: 样本图像列表
    :param max_samples: 最大样本数量（默认20帧）
    :return: 检测到的语言代码列表
    """
    try:
        # 使用默认语言进行初步检测（中英文）
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
            print(f"语言检测样本 {i+1}: {text[:30]}...")
            
            # 简单的字符集检测
            chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
            english_chars = len(re.findall(r'[a-zA-Z]', text))
            
            if chinese_chars > 0:
                chinese_count += 1
            if english_chars > 0:
                english_count += 1
        
        print(f"语言检测结果: 中文={chinese_count}, 英文={english_count}, 总处理样本={total_processed}")
        
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
        print(f"警告: 语言检测失败: {e}，使用默认语言")
        return constants.DEFAULT_OCR_LANGUAGES


def _convert_pgs_timestamp_to_srt(pts_time):
    """
    将 PGS 时间戳转换为 SRT 格式
    注意：pgsreader 输出的是毫秒单位（不是秒！）
    SRT: HH:MM:SS,mmm 格式
    """
    try:
        # 检查输入值是否合理
        if pts_time < 0:
            print(f"警告: 负数时间戳: {pts_time}")
            pts_time = 0
        
        # PGS Reader 输出的实际上是毫秒，不是秒！
        total_ms = int(pts_time)  # 直接使用，不再乘以1000
        
        # 计算小时、分钟、秒、毫秒
        hours = total_ms // 3600000
        minutes = (total_ms % 3600000) // 60000
        seconds = (total_ms % 60000) // 1000
        milliseconds = total_ms % 1000
        
        # 格式化为 SRT 时间格式
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
        
    except Exception as e:
        print(f"警告: 时间戳转换失败 (pts_time={pts_time}): {e}")
        return "00:00:00,000"


def parse_sup_to_srt_structure(file_path, target_language=None, progress_callback=None):
    """
    解析 SUP 文件并转换为标准 SRT 数据结构
    
    :param file_path: SUP 文件路径
    :param target_language: 目标语言代码，None 时自动检测
    :param progress_callback: 进度回调函数 callback(current, total, message)
    :return: List[List[str]]: [序号, 开始时间, 结束时间, 字幕内容]
    :raises SupParseError: 当解析过程出错时
    """
    try:
        print(f"开始解析 SUP 文件: {file_path}")
        
        # 1. 初始化 PGS 读取器
        pgs_reader = PGSReader(file_path)
        displaysets = pgs_reader.displaysets
        
        if not displaysets:
            raise SupParseError("无法从 SUP 文件中提取字幕数据")
        
        print(f"找到 {len(displaysets)} 个字幕帧")
        
        # 进度回调：开始解析
        if progress_callback:
            progress_callback(0, len(displaysets), "开始解析 SUP 文件...", phase="file_parsing")
        
        # 2. 预处理：提取样本图像用于语言检测
        sample_images = []
        for i, ds in enumerate(displaysets[:20]):  # 前20帧用于检测（增加样本量）
            try:
                pcs = next((s for s in ds.segments if s.type == 'PCS'), None)
                pds = next((s for s in ds.segments if s.type == 'PDS'), None)
                ods = next((s for s in ds.segments if s.type == 'ODS'), None)
                
                if pcs and pds and ods:
                    image = make_image(ods, pds)
                    sample_images.append(image)
            except Exception as e:
                print(f"警告: 提取样本图像 {i} 失败: {e}")
                continue
        
        # 3. 语言检测
        if progress_callback:
            progress_callback(0, len(displaysets), "正在检测字幕语言...", phase="language_detection")
        
        if target_language is None:
            detected_languages = _detect_subtitle_language(sample_images)
            print(f"检测到的语言: {detected_languages}")
        else:
            detected_languages = [target_language] if isinstance(target_language, str) else target_language
        
        # 4. 初始化 OCR 引擎
        if progress_callback:
            progress_callback(0, len(displaysets), f"初始化 OCR 引擎（语言: {detected_languages}）...", phase="ocr_init")
        
        ocr_engine = SupOcrEngine(detected_languages)
        
        # 5. 遍历所有 DisplaySet，提取字幕数据
        data = []
        subtitle_count = 0  # 改为从0开始计数
        first_valid_pts = None  # 记录第一个有效字幕的时间戳，用于对比分析
        
        for i, ds in enumerate(displaysets):
            # 进度回调：处理帧进度
            if progress_callback:
                percentage = int((i / len(displaysets)) * 100)
                progress_callback(i + 1, len(displaysets), f"正在处理第 {i+1}/{len(displaysets)} 帧...", 
                                current_frame=i + 1, total_frames=len(displaysets), 
                                phase="ocr_processing", percentage=percentage, subtitle_count=subtitle_count)
            
            try:
                # 提取各种段
                pcs = next((s for s in ds.segments if s.type == 'PCS'), None)
                pds = next((s for s in ds.segments if s.type == 'PDS'), None)
                ods = next((s for s in ds.segments if s.type == 'ODS'), None)
                
                if not (pcs and pds and ods):
                    print(f"警告: 帧 {i} 缺少必要的段，跳过")
                    continue
                
                # 提取时间戳（使用 PCS 的时间戳）
                start_pts = pcs.pts
                
                # 记录第一个有效字幕的时间戳
                if first_valid_pts is None:
                    # 先检查这个帧是否有效字幕
                    try:
                        image = make_image(ods, pds)
                        temp_text = ocr_engine.recognize_subtitle_text(image)
                        if temp_text.strip():
                            first_valid_pts = start_pts
                            print(f"第一个有效字幕的时间戳: {first_valid_pts} 秒")
                    except:
                        pass
                
                # 调试信息：显示原始时间戳值
                if i < 5:  # 显示前5帧的调试信息
                    converted_time = _convert_pgs_timestamp_to_srt(start_pts)
                    print(f"调试: 帧 {i} - 原始 PTS: {start_pts}, 转换后: {converted_time}")
                
                # 查找下一个 DisplaySet 的时间戳作为结束时间
                if i + 1 < len(displaysets):
                    next_pcs = next((s for s in displaysets[i + 1].segments if s.type == 'PCS'), None)
                    end_pts = next_pcs.pts if next_pcs else start_pts + 2000  # 默认2秒（毫秒单位）
                else:
                    end_pts = start_pts + 2000  # 最后一帧，默认显示2秒
                
                # 转换时间格式
                start_time = _convert_pgs_timestamp_to_srt(start_pts)
                end_time = _convert_pgs_timestamp_to_srt(end_pts)
                
                # 生成图像
                image = make_image(ods, pds)
                
                # OCR 识别
                text = ocr_engine.recognize_subtitle_text(image)
                
                # 过滤空文本
                if text.strip():
                    subtitle_count += 1  # 增加字幕计数
                    data.append([str(subtitle_count), start_time, end_time, text.strip()])
                    print(f"提取字幕 {subtitle_count}: {text.strip()[:50]}...")
                    
                    # 立即更新进度回调，包含最新的字幕数量
                    if progress_callback:
                        percentage = int((i / len(displaysets)) * 100)
                        progress_callback(i + 1, len(displaysets), f"正在处理第 {i+1}/{len(displaysets)} 帧... (已识别 {subtitle_count} 条字幕)", 
                                        current_frame=i + 1, total_frames=len(displaysets), 
                                        phase="ocr_processing", percentage=percentage, subtitle_count=subtitle_count)
                
            except Exception as e:
                print(f"警告: 处理帧 {i} 时出错: {e}，跳过")
                continue
        
        print(f"SUP 解析完成，共提取到 {subtitle_count} 条字幕")
        
        # 进度回调：完成
        if progress_callback:
            progress_callback(len(displaysets), len(displaysets), f"解析完成！共提取到 {subtitle_count} 条字幕", 
                            current_frame=len(displaysets), total_frames=len(displaysets), 
                            phase="complete", percentage=100, subtitle_count=subtitle_count)
        
        return data
        
    except Exception as e:
        raise SupParseError(f"解析 SUP 文件 '{file_path}' 时出错: {e}") from e


def _convert_ass_time_to_srt(ass_time):
    """
    一个内部辅助函数，用于将ASS时间格式转换为SRT时间格式。
    例如，它能将 "0:00:06.40" 转换为 "00:00:06,400"。
    :param ass_time: ASS格式的时间字符串。
    :return: SRT格式的时间字符串。
    """
    try:
        # 按小数点分割时间的主体部分和厘秒(cs)部分
        hms_part, cs_part = ass_time.split('.')

        # 按冒号分割小时、分钟、秒
        time_components = hms_part.split(':')

        # 使用 zfill(2) 方法确保小时、分钟、秒都是两位数，不足则在左侧补零
        h = time_components[0].zfill(2)
        m = time_components[1].zfill(2)
        s = time_components[2].zfill(2)

        # 使用 ljust(3, '0') 将厘秒(2位)转换为毫秒(3位)，通过在右侧补零
        ms_part = cs_part.ljust(3, '0')

        # 按SRT格式重新组合，并用逗号分隔秒和毫秒
        return f"{h}:{m}:{s},{ms_part}"
    except Exception:
        # 如果转换过程中出现任何意外（如不规范的时间格式），返回原始时间，以防程序崩溃
        return ass_time


def parse_ass_to_srt_structure(file_path):
    """
    解析 .ass 文件，并将其内容转换为SRT的标准数据结构。
    这种方法非常稳健，因为它只关注我们需要的字段，忽略其他复杂信息。
    :param file_path: .ass 文件的路径。
    :return: 一个二维列表，格式与 parse_srt 的返回结果完全相同。
    :raises ParseError: 当解析过程出错时（例如缺少关键字段）。
    """
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
    except Exception as e:
        raise ParseError(f"读取 ASS 文件 '{file_path}' 时出错: {e}") from e

    # --- 使用状态机思想进行解析 ---
    in_events_section = False  # 一个标志，用于判断当前是否在 [Events] 段落内
    format_map = {}            # 一个字典，用于存储 Format 行定义的字段顺序
    dialogue_count = 1         # 手动为每一行字幕生成序号

    for line in lines:
        line = line.strip() # 去除行首尾的空白字符
        if line.lower() == '[events]':
            in_events_section = True
            continue # 进入下一轮循环

        if not in_events_section:
            continue # 如果还没到 [Events] 段，就忽略当前行

        if line.lower().startswith('format:'):
            # 解析 Format 行，这决定了 Dialogue 行的数据顺序
            fields = [field.strip().lower() for field in line.split(':', 1)[1].split(',')]
            # 创建一个从字段名到其索引位置的映射，如 {'start': 1, 'end': 2, 'text': 9}
            format_map = {field: i for i, field in enumerate(fields)}
            if 'start' not in format_map or 'end' not in format_map or 'text' not in format_map:
                raise ParseError("ASS 'Format' 行缺少 Start, End, 或 Text 关键字段。")

        elif line.lower().startswith('dialogue:') and format_map:
            # 只处理 Dialogue 行，并且前提是已经解析过 Format 行
            # 这是最关键的一步：只在 Text 字段之前进行分割。
            # maxsplit 参数确保了字幕内容中的逗号不会被错误地分割。
            try:
                parts = line.split(':', 1)[1].strip().split(',', len(format_map) - 1)
            except Exception as e:
                # 如果分割出错，跳过这一行并记录警告
                print(f"警告: 解析 Dialogue 行时出错，已跳过: {line}. 错误: {e}")
                continue

            # 根据之前创建的映射，从 parts 列表中安全地提取数据
            try:
                ass_start_time = parts[format_map['start']]
                ass_end_time = parts[format_map['end']]

                # 调用辅助函数，将ASS时间转换为SRT标准格式
                start_time = _convert_ass_time_to_srt(ass_start_time)
                end_time = _convert_ass_time_to_srt(ass_end_time)

                raw_text = parts[format_map['text']]
                # 使用正则表达式清除ASS特效标签，如 {\fad(200,200)} 或 {\an8}
                clean_text = re.sub(r'\{.*?\}', '', raw_text)
                # ASS中的换行符是 \N 或 \n，都替换为空格
                clean_text = clean_text.replace('\\N', ' ').replace('\\n', ' ')

                # 将处理好的数据存入列表，格式与SRT解析结果统一
                data.append([str(dialogue_count), start_time, end_time, clean_text])
                dialogue_count += 1 # 序号加一
            except (IndexError, KeyError) as e:
                # 如果字段访问出错，跳过这一行并记录警告
                print(f"警告: Dialogue 行字段不完整或格式错误，已跳过: {line}. 错误: {e}")
                continue
            except Exception as e:
                # 其他与处理相关的错误
                print(f"警告: 处理 Dialogue 行时出错，已跳过: {line}. 错误: {e}")
                continue

    return data