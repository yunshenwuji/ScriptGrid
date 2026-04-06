"""
字幕解析模块
负责将 .srt, .ass, .sup, .xlsx 格式的字幕文件解析为统一的内部数据结构。
内部数据结构: List[List[str]],每个子列表代表一行字幕,格式为 [index, start_time, end_time, text]。
"""

from parsers.srt_parser import parse_srt
from parsers.ass_parser import parse_ass_to_srt_structure
from parsers.sup_parser import parse_sup_to_srt_structure
from parsers.xlsx_parser import parse_xlsx

__all__ = [
    'parse_srt',
    'parse_ass_to_srt_structure', 
    'parse_sup_to_srt_structure',
    'parse_xlsx'
]
