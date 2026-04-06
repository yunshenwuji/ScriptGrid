"""
SUP 字幕解析器
负责将 .sup (PGS) 格式的字幕文件解析并OCR识别为统一的内部数据结构。
"""

import os
import logging
from exceptions import SupParseError
from pgsreader import PGSReader
from imagemaker import make_image
from ocr.engine import SupOcrEngine
from ocr.language_detector import detect_subtitle_language
import constants

# 配置日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def _convert_pgs_timestamp_to_srt(pts_time):
    """
    将 PGS 时间戳转换为 SRT 格式
    注意:pgsreader 输出的是毫秒单位(不是秒!)
    SRT: HH:MM:SS,mmm 格式
    """
    try:
        # 检查输入值是否合理
        if pts_time < 0:
            logger.warning(f"负数时间戳: {pts_time}")
            pts_time = 0
        
        # PGS Reader 输出的实际上是毫秒,不再乘以1000
        total_ms = int(pts_time)
        
        # 计算小时、分钟、秒、毫秒
        hours = total_ms // 3600000
        minutes = (total_ms % 3600000) // 60000
        seconds = (total_ms % 60000) // 1000
        milliseconds = total_ms % 1000
        
        # 格式化为 SRT 时间格式
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
        
    except Exception as e:
        logger.warning(f"时间戳转换失败 (pts_time={pts_time}): {e}")
        return "00:00:00,000"


def parse_sup_to_srt_structure(file_path, target_language=None, progress_callback=None):
    """
    解析 SUP 文件并转换为标准 SRT 数据结构
    
    :param file_path: SUP 文件路径
    :param target_language: 目标语言代码,None 时自动检测
    :param progress_callback: 进度回调函数 callback(current, total, message)
    :return: List[List[str]]: [序号, 开始时间, 结束时间, 字幕内容]
    :raises SupParseError: 当解析过程出错时
    """
    try:
        logger.info(f"开始解析 SUP 文件: {file_path}")
        
        # 1. 初始化 PGS 读取器
        pgs_reader = PGSReader(file_path)
        displaysets = pgs_reader.displaysets
        
        if not displaysets:
            raise SupParseError("无法从 SUP 文件中提取字幕数据")
        
        logger.info(f"找到 {len(displaysets)} 个字幕帧")
        
        # 进度回调:开始解析
        if progress_callback:
            progress_callback(0, len(displaysets), "开始解析 SUP 文件...", phase="file_parsing")
        
        # 2. 预处理:提取样本图像用于语言检测
        sample_images = []
        for i, ds in enumerate(displaysets[:20]):  # 前20帧用于检测(增加样本量)
            try:
                pcs = next((s for s in ds.segments if s.type == 'PCS'), None)
                pds = next((s for s in ds.segments if s.type == 'PDS'), None)
                ods = next((s for s in ds.segments if s.type == 'ODS'), None)
                
                if pcs and pds and ods:
                    image = make_image(ods, pds)
                    sample_images.append(image)
            except Exception as e:
                logger.warning(f"提取样本图像 {i} 失败: {e}")
                continue
        
        # 3. 语言检测
        if progress_callback:
            progress_callback(0, len(displaysets), "正在检测字幕语言...", phase="language_detection")
        
        if target_language is None:
            detected_languages = detect_subtitle_language(sample_images)
            logger.info(f"检测到的语言: {detected_languages}")
        else:
            detected_languages = [target_language] if isinstance(target_language, str) else target_language
        
        # 4. 初始化 OCR 引擎
        if progress_callback:
            progress_callback(0, len(displaysets), f"初始化 OCR 引擎(语言: {detected_languages})...", phase="ocr_init")
        
        ocr_engine = SupOcrEngine(detected_languages)
        
        # 5. 遍历所有 DisplaySet,提取字幕数据
        data = []
        subtitle_count = 0  # 改为从0开始计数
        first_valid_pts = None  # 记录第一个有效字幕的时间戳,用于对比分析
        
        for i, ds in enumerate(displaysets):
            # 进度回调:处理帧进度
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
                    logger.warning(f"帧 {i} 缺少必要的段,跳过")
                    continue
                
                # 提取时间戳(使用 PCS 的时间戳)
                start_pts = pcs.pts
                
                # 记录第一个有效字幕的时间戳
                if first_valid_pts is None:
                    # 先检查这个帧是否有效字幕
                    try:
                        image = make_image(ods, pds)
                        temp_text = ocr_engine.recognize_subtitle_text(image)
                        if temp_text.strip():
                            first_valid_pts = start_pts
                            logger.info(f"第一个有效字幕的时间戳: {first_valid_pts} 秒")
                    except Exception:
                        pass
                
                # 查找下一个 DisplaySet 的时间戳作为结束时间
                if i + 1 < len(displaysets):
                    next_pcs = next((s for s in displaysets[i + 1].segments if s.type == 'PCS'), None)
                    end_pts = next_pcs.pts if next_pcs else start_pts + 2000  # 默认2秒(毫秒单位)
                else:
                    end_pts = start_pts + 2000  # 最后一帧,默认显示2秒
                
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
                    logger.info(f"提取字幕 {subtitle_count}: {text.strip()[:50]}...")
                    
                    # 立即更新进度回调,包含最新的字幕数量
                    if progress_callback:
                        percentage = int((i / len(displaysets)) * 100)
                        progress_callback(i + 1, len(displaysets), f"正在处理第 {i+1}/{len(displaysets)} 帧... (已识别 {subtitle_count} 条字幕)", 
                                        current_frame=i + 1, total_frames=len(displaysets), 
                                        phase="ocr_processing", percentage=percentage, subtitle_count=subtitle_count)
                
            except Exception as e:
                logger.warning(f"处理帧 {i} 时出错: {e},跳过")
                continue
        
        logger.info(f"SUP 解析完成,共提取到 {subtitle_count} 条字幕")
        
        # 进度回调:完成
        if progress_callback:
            progress_callback(len(displaysets), len(displaysets), f"解析完成!共提取到 {subtitle_count} 条字幕", 
                            current_frame=len(displaysets), total_frames=len(displaysets), 
                            phase="complete", percentage=100, subtitle_count=subtitle_count)
        
        return data
        
    except Exception as e:
        raise SupParseError(f"解析 SUP 文件 '{file_path}' 时出错: {e}") from e
