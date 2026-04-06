"""
ASS 字幕解析器
负责将 .ass 格式的字幕文件解析为统一的内部数据结构。
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


def _convert_ass_time_to_srt(ass_time):
    """
    一个内部辅助函数,用于将ASS时间格式转换为SRT时间格式。
    例如,它能将 "0:00:06.40" 转换为 "00:00:06,400"。
    :param ass_time: ASS格式的时间字符串。
    :return: SRT格式的时间字符串。
    """
    try:
        # 按小数点分割时间的主体部分和厘秒(cs)部分
        hms_part, cs_part = ass_time.split('.')

        # 按冒号分割小时、分钟、秒
        time_components = hms_part.split(':')

        # 使用 zfill(2) 方法确保小时、分钟、秒都是两位数,不足则在左侧补零
        h = time_components[0].zfill(2)
        m = time_components[1].zfill(2)
        s = time_components[2].zfill(2)

        # 使用 ljust(3, '0') 将厘秒(2位)转换为毫秒(3位),通过在右侧补零
        ms_part = cs_part.ljust(3, '0')

        # 按SRT格式重新组合,并用逗号分隔秒和毫秒
        return f"{h}:{m}:{s},{ms_part}"
    except Exception:
        # 如果转换过程中出现任何意外(如不规范的时间格式),返回原始时间,以防程序崩溃
        return ass_time


def parse_ass_to_srt_structure(file_path):
    """
    解析 .ass 文件,并将其内容转换为SRT的标准数据结构。
    这种方法非常稳健,因为它只关注我们需要的字段,忽略其他复杂信息。
    :param file_path: .ass 文件的路径。
    :return: 一个二维列表,格式与 parse_srt 的返回结果完全相同。
    :raises ParseError: 当解析过程出错时(例如缺少关键字段)。
    """
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
    except Exception as e:
        raise ParseError(f"读取 ASS 文件 '{file_path}' 时出错: {e}") from e

    # --- 使用状态机思想进行解析 ---
    in_events_section = False  # 一个标志,用于判断当前是否在 [Events] 段落内
    format_map = {}            # 一个字典,用于存储 Format 行定义的字段顺序
    dialogue_count = 1         # 手动为每一行字幕生成序号

    for line in lines:
        line = line.strip() # 去除行首尾的空白字符
        if line.lower() == '[events]':
            in_events_section = True
            continue # 进入下一轮循环

        if not in_events_section:
            continue # 如果还没到 [Events] 段,就忽略当前行

        if line.lower().startswith('format:'):
            # 解析 Format 行,这决定了 Dialogue 行的数据顺序
            fields = [field.strip().lower() for field in line.split(':', 1)[1].split(',')]
            # 创建一个从字段名到其索引位置的映射,如 {'start': 1, 'end': 2, 'text': 9}
            format_map = {field: i for i, field in enumerate(fields)}
            if 'start' not in format_map or 'end' not in format_map or 'text' not in format_map:
                raise ParseError("ASS 'Format' 行缺少 Start, End, 或 Text 关键字段。")

        elif line.lower().startswith('dialogue:') and format_map:
            # 只处理 Dialogue 行,并且前提是已经解析过 Format 行
            # 这是最关键的一步:只在 Text 字段之前进行分割。
            # maxsplit 参数确保了字幕内容中的逗号不会被错误地分割。
            try:
                parts = line.split(':', 1)[1].strip().split(',', len(format_map) - 1)
            except Exception as e:
                # 如果分割出错,跳过这一行并记录警告
                logger.warning(f"解析 Dialogue 行时出错,已跳过: {line}. 错误: {e}")
                continue

            # 根据之前创建的映射,从 parts 列表中安全地提取数据
            try:
                ass_start_time = parts[format_map['start']]
                ass_end_time = parts[format_map['end']]

                # 调用辅助函数,将ASS时间转换为SRT标准格式
                start_time = _convert_ass_time_to_srt(ass_start_time)
                end_time = _convert_ass_time_to_srt(ass_end_time)

                raw_text = parts[format_map['text']]
                # 使用正则表达式清除ASS特效标签,如 {\fad(200,200)} 或 {\an8}
                clean_text = re.sub(r'\{.*?\}', '', raw_text)
                # 将ASS中的换行符 \N 和 \n 转换为实际的换行符
                clean_text = clean_text.replace('\\N', '\n').replace('\\n', '\n')

                # 将处理好的数据存入列表,格式与SRT解析结果统一
                data.append([str(dialogue_count), start_time, end_time, clean_text])
                dialogue_count += 1 # 序号加一
            except (IndexError, KeyError) as e:
                # 如果字段访问出错,跳过这一行并记录警告
                logger.warning(f"Dialogue 行字段不完整或格式错误,已跳过: {line}. 错误: {e}")
                continue
            except Exception as e:
                # 其他与处理相关的错误
                logger.warning(f"处理 Dialogue 行时出错,已跳过: {line}. 错误: {e}")
                continue

    return data
