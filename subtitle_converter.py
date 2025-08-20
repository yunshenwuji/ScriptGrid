# -*- coding: utf-8 -*-

"""
核心转换逻辑模块 (适用于 Web 后端)
负责协调解析和写入过程。
"""

# Note: This file is largely unchanged from the original, 
# but we ensure it's compatible with being called by the web backend.
# The main change is to make path handling more robust and add logging.

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
# We assume these are in the same directory or PYTHONPATH
from parsers import parse_srt, parse_ass_to_srt_structure
from writers import write_to_excel, write_to_srt, parse_xlsx
from exceptions import SubtitleConverterError, ParseError, WriteError
import constants


def convert(input_path: str, output_path: str, conversion_type: str) -> None:
    """
    执行字幕文件的转换。
    :param input_path: 输入文件的完整路径。
    :param output_path: 输出文件的完整路径。
    :param conversion_type: 转换类型。
                        'subtitle_to_excel': .srt/.ass -> .xlsx
                        'ass_to_srt': .ass -> .srt
                        'xlsx_to_srt': .xlsx -> .srt
    :raises SubtitleConverterError: 转换过程中发生的任何错误。
    """
    logger.info(f"Starting conversion: {input_path} -> {output_path} (type: {conversion_type})")
    data: List[List[str]] = []
    try:
        # --- 1. 解析阶段 ---
        if conversion_type == 'subtitle_to_excel':
            if input_path.lower().endswith('.srt'):
                data = parse_srt(input_path)
            elif input_path.lower().endswith('.ass'):
                data = parse_ass_to_srt_structure(input_path)
            else:
                raise SubtitleConverterError(constants.MSG_WARNING_UNSUPPORTED_FORMAT)

        elif conversion_type == 'ass_to_srt':
            if input_path.lower().endswith('.ass'):
                data = parse_ass_to_srt_structure(input_path)
            else:
                raise SubtitleConverterError("输入文件必须是 .ass 格式。")

        elif conversion_type == 'xlsx_to_srt':
            if input_path.lower().endswith('.xlsx'):
                data = parse_xlsx(input_path)
            else:
                raise SubtitleConverterError("输入文件必须是 .xlsx 格式。")

        else:
            raise SubtitleConverterError(f"不支持的转换类型: {conversion_type}")

        # --- 2. 检查解析结果 ---
        if not data:
            logger.warning("No data parsed from the input file.")
            raise SubtitleConverterError(constants.MSG_WARNING_NO_DATA_PARSED)

        # --- 3. 写入阶段 ---
        if conversion_type == 'subtitle_to_excel':
            write_to_excel(data, output_path)
        elif conversion_type in ['ass_to_srt', 'xlsx_to_srt']:
            write_to_srt(data, output_path)
        
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