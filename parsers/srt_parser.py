"""
SRT 字幕解析器
负责将 .srt 格式的字幕文件解析为统一的内部数据结构。
"""

import re
import logging
from exceptions import ParseError

# 配置日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def parse_srt(file_path):
    """
    解析 .srt 字幕文件。
    :param file_path: .srt 文件的路径。
    :return: 一个二维列表,每个子列表代表一行字幕:[序号, 开始时间, 结束时间, 字幕内容]。
    :raises ParseError: 当解析过程出错时。
    """
    try:
        # 使用 'utf-8-sig' 编码读取文件,可以正确处理可能存在的BOM头
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        # 定义一个强大的正则表达式来匹配一个完整的SRT字幕块
        # re.DOTALL 标志让 '.' 可以匹配包括换行符在内的任意字符
        pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?:\n\n|\n?$)', re.DOTALL)
        # 找到所有匹配项
        matches = pattern.findall(content)

        data = [] # 准备存放结果
        for match in matches:
            # match 是一个元组,包含了正则表达式中每个括号捕获到的内容
            index = match[0]
            start_time = match[1]
            end_time = match[2]
            # 保持原始的换行符,不将其替换为空格
            text = match[3].replace('\r\n', '\n')
            data.append([index, start_time, end_time, text])

        return data
    except Exception as e:
        raise ParseError(f"解析 SRT 文件 '{file_path}' 时出错: {e}") from e
