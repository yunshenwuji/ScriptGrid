# -*- coding: utf-8 -*-

"""
核心转换逻辑模块 (适用于 Web 后端)
负责协调解析和写入过程。
"""

import os
import logging
from typing import List

# Configure logger for this module
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


# Import local modules
from parsers import parse_srt, parse_ass_to_srt_structure, parse_sup_to_srt_structure, parse_xlsx
from writers import write_to_excel, write_to_srt
from exceptions import SubtitleConverterError, ParseError, WriteError
import constants


def srt_time_to_ms(time_str: str) -> int:
    """
    将 SRT 时间字符串 "HH:MM:SS,mmm" 转换为毫秒整数。
    :param time_str: 时间字符串，格式 "HH:MM:SS,mmm"
    :return: 毫秒整数
    """
    time_str = time_str.replace('.', ',')
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds_ms = parts[2].split(',')
    seconds = int(seconds_ms[0])
    milliseconds = int(seconds_ms[1]) if len(seconds_ms) > 1 else 0
    return hours * 3600000 + minutes * 60000 + seconds * 1000 + milliseconds


def ms_to_srt_time(ms: int) -> str:
    """
    将毫秒整数转换为 SRT 时间字符串 "HH:MM:SS,mmm"。
    :param ms: 毫秒整数
    :return: 时间字符串，格式 "HH:MM:SS,mmm"
    """
    hours = ms // 3600000
    ms %= 3600000
    minutes = ms // 60000
    ms %= 60000
    seconds = ms // 1000
    milliseconds = ms % 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def generate_narration_timing(subtitles: List[List[str]], placeholder_text: str = "请填写口述文本") -> List[List[str]]:
    """
    根据字幕数据生成口述稿时间轴。
    
    算法：
    - 片头时间: 00:00:00,000
    - 片尾时间: 最后一条字幕的结束时间（不在片尾之后生成口述稿）
    - 第一段口述稿: 开始=00:00:00,000，结束=第一条字幕开始时间 - 500ms
    - 中间段口述稿: 开始=前一条字幕结束时间 + 500ms，结束=后一条字幕开始时间 - 500ms
    - 不需要在最后一条字幕之后生成口述稿
    - 过滤: 仅保留持续时间 >= 1000ms (1秒) 的口述稿字幕
    
    :param subtitles: 已解析的 SRT 字幕数据，格式: [[index, start_time, end_time, text], ...]
    :param placeholder_text: 口述稿文本内容
    :return: 口述稿字幕数据，格式与输入相同，index 从 "1" 开始重新编号
    """
    if not subtitles:
        return []
    
    narration_segments = []
    
    # 片头时间
    header_time_ms = 0
    
    # 处理第一段口述稿（从片头到第一条字幕）
    first_subtitle_start_ms = srt_time_to_ms(subtitles[0][1])
    first_narration_end_ms = first_subtitle_start_ms - 500
    
    if first_narration_end_ms - header_time_ms >= 1000:
        narration_segments.append([
            "1",
            ms_to_srt_time(header_time_ms),
            ms_to_srt_time(first_narration_end_ms),
            placeholder_text
        ])
    
    # 处理中间段口述稿
    for i in range(len(subtitles) - 1):
        current_subtitle_end_ms = srt_time_to_ms(subtitles[i][2])
        next_subtitle_start_ms = srt_time_to_ms(subtitles[i + 1][1])
        
        narration_start_ms = current_subtitle_end_ms + 500
        narration_end_ms = next_subtitle_start_ms - 500
        
        if narration_end_ms - narration_start_ms >= 1000:
            narration_segments.append([
                str(len(narration_segments) + 1),
                ms_to_srt_time(narration_start_ms),
                ms_to_srt_time(narration_end_ms),
                placeholder_text
            ])
    
    # 注意：不在最后一条字幕之后生成口述稿（片尾）
    
    return narration_segments


def _parse_input_file(input_path: str, conversion_type: str, progress_callback=None, target_language=None) -> List[List[str]]:
    """
    统一的解析阶段逻辑
    :param input_path: 输入文件路径
    :param conversion_type: 转换类型
    :param progress_callback: 进度回调函数(可选)
    :param target_language: 目标语言(仅SUP转换)
    :return: 解析后的字幕数据
    """
    data: List[List[str]] = []
    
    # SRT/ASS -> Excel
    if conversion_type == 'subtitle_to_excel':
        if input_path.lower().endswith('.srt'):
            data = parse_srt(input_path)
        elif input_path.lower().endswith('.ass'):
            data = parse_ass_to_srt_structure(input_path)
        else:
            raise SubtitleConverterError(constants.MSG_WARNING_UNSUPPORTED_FORMAT)
    
    # ASS -> SRT
    elif conversion_type == 'ass_to_srt':
        if input_path.lower().endswith('.ass'):
            data = parse_ass_to_srt_structure(input_path)
        else:
            raise SubtitleConverterError("输入文件必须是 .ass 格式。")
    
    # XLSX -> SRT
    elif conversion_type == 'xlsx_to_srt':
        if input_path.lower().endswith('.xlsx'):
            data = parse_xlsx(input_path)
        else:
            raise SubtitleConverterError("输入文件必须是 .xlsx 格式。")
    
    # SUP -> SRT/Excel (支持进度回调)
    elif conversion_type in ['sup_to_srt', 'sup_to_excel']:
        if input_path.lower().endswith('.sup'):
            data = parse_sup_to_srt_structure(
                input_path, 
                target_language=target_language, 
                progress_callback=progress_callback
            )
        else:
            raise SubtitleConverterError("输入文件必须是 .sup 格式。")
    
    # 自动口述稿打轴
    elif conversion_type == 'auto_narration_timing':
        if input_path.lower().endswith('.srt'):
            data = parse_srt(input_path)
        elif input_path.lower().endswith('.ass'):
            data = parse_ass_to_srt_structure(input_path)
        elif input_path.lower().endswith('.sup'):
            data = parse_sup_to_srt_structure(
                input_path, 
                target_language=target_language, 
                progress_callback=progress_callback
            )
        else:
            raise SubtitleConverterError("自动口述稿功能仅支持 .srt、.ass 和 .sup 文件。")
    
    else:
        raise SubtitleConverterError(f"不支持的转换类型: {conversion_type}")
    
    # 检查解析结果
    if not data:
        logger.warning("No data parsed from the input file.")
        raise SubtitleConverterError(constants.MSG_WARNING_NO_DATA_PARSED)
    
    return data


def _write_output_file(data: List[List[str]], output_path: str, conversion_type: str, placeholder_text: str = "请填写口述文本") -> None:
    """
    统一的写入阶段逻辑
    :param data: 字幕数据
    :param output_path: 输出文件路径
    :param conversion_type: 转换类型
    :param placeholder_text: 口述稿占位文本
    """
    # 转Excel
    if conversion_type in ['subtitle_to_excel', 'sup_to_excel']:
        write_to_excel(data, output_path)
    
    # 转SRT
    elif conversion_type in ['ass_to_srt', 'xlsx_to_srt', 'sup_to_srt']:
        write_to_srt(data, output_path)
    
    # 自动口述稿打轴
    elif conversion_type == 'auto_narration_timing':
        narration_data = generate_narration_timing(data, placeholder_text)
        if not narration_data:
            logger.warning("No narration timing generated from the input file.")
            raise SubtitleConverterError("没有生成口述稿时间轴，可能没有足够的空白时间段。")
        write_to_srt(narration_data, output_path)
    
    else:
        raise SubtitleConverterError(f"不支持的转换类型: {conversion_type}")


def convert(input_path: str, output_path: str, conversion_type: str, placeholder_text: str = "请填写口述文本") -> None:
    """
    执行字幕文件的转换。
    :param input_path: 输入文件的完整路径。
    :param output_path: 输出文件的完整路径。
    :param conversion_type: 转换类型。
                        'subtitle_to_excel': .srt/.ass -> .xlsx
                        'ass_to_srt': .ass -> .srt
                        'xlsx_to_srt': .xlsx -> .srt
                        'sup_to_srt': .sup -> .srt
                        'sup_to_excel': .sup -> .xlsx
                        'auto_narration_timing': .srt/.ass -> 口述稿.srt
    :param placeholder_text: 口述稿占位文本（仅用于 auto_narration_timing）
    :raises SubtitleConverterError: 转换过程中发生的任何错误。
    """
    logger.info(f"Starting conversion: {input_path} -> {output_path} (type: {conversion_type})")
    
    try:
        # 1. 解析阶段
        data = _parse_input_file(input_path, conversion_type)
        
        # 2. 写入阶段
        _write_output_file(data, output_path, conversion_type, placeholder_text)
        
        logger.info(f"Conversion successful: {output_path}")
        
    except (ParseError, WriteError) as e:
        # 重新抛出为更通用的转换错误
        logger.error(f"Parse/Write error during conversion: {e}")
        raise SubtitleConverterError(str(e)) from e
    except SubtitleConverterError:
        # 重新抛出我们自定义的错误
        logger.error("SubtitleConverterError occurred.")
        raise
    except Exception as e:
        # 捕获所有其他未预期的错误
        logger.error(f"Unexpected error during conversion: {e}")
        raise SubtitleConverterError(f"转换过程中发生未预期的错误: {e}") from e


def convert_with_progress(input_path: str, output_path: str, conversion_type: str, progress_callback=None, target_language=None, placeholder_text: str = "请填写口述文本") -> None:
    """
    执行字幕文件的转换（带进度回调）。
    :param input_path: 输入文件的完整路径。
    :param output_path: 输出文件的完整路径。
    :param conversion_type: 转换类型。
    :param progress_callback: 进度回调函数 callback(current, total, message)
    :param target_language: 目标语言代码，None 时自动检测
    :param placeholder_text: 口述稿占位文本（仅用于 auto_narration_timing）
    :raises SubtitleConverterError: 转换过程中发生的任何错误。
    """
    logger.info(f"Starting conversion with progress: {input_path} -> {output_path} (type: {conversion_type})")
    
    try:
        # 1. 解析阶段(支持进度回调)
        data = _parse_input_file(input_path, conversion_type, progress_callback, target_language)
        
        # 2. 写入阶段
        _write_output_file(data, output_path, conversion_type, placeholder_text)
        
        logger.info(f"Conversion with progress successful: {output_path}")
        
    except (ParseError, WriteError) as e:
        # 重新抛出为更通用的转换错误
        logger.error(f"Parse/Write error during conversion: {e}")
        raise SubtitleConverterError(str(e)) from e
    except SubtitleConverterError:
        # 重新抛出我们自定义的错误
        logger.error("SubtitleConverterError occurred.")
        raise
    except Exception as e:
        # 捕获所有其他未预期的错误
        logger.error(f"Unexpected error during conversion: {e}")
        raise SubtitleConverterError(f"转换过程中发生未预期的错误: {e}") from e