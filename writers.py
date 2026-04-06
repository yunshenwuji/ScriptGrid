"""
文件写入模块
负责将内部数据结构写入 .xlsx 或 .srt 文件。
"""

import os
from openpyxl import Workbook
from exceptions import WriteError
import constants

# 从 parsers 包导入 parse_xlsx 以保持向后兼容
from parsers import parse_xlsx

def write_to_excel(data, output_path):
    """
    将提取的数据写入一个 .xlsx 文件。
    :param data: 包含所有字幕信息的二维列表。
    :param output_path: 输出的 .xlsx 文件的完整路径。
    :raises WriteError: 当写入过程出错时。
    """
    try:
        wb = Workbook() # 创建一个新的Excel工作簿
        ws = wb.active  # 获取当前活动的工作表
        ws.title = constants.EXCEL_SHEET_NAME # 根据常量设置工作表名称

        # 写入表头
        ws.append(constants.EXCEL_HEADERS) # append 方法可以直接写入一行

        # 遍历数据，将每一行字幕写入Excel工作表
        for row_data in data:
            ws.append(row_data)

        # 保存工作簿到指定的路径，如果文件已存在则会覆盖
        wb.save(output_path)
    except Exception as e:
        raise WriteError(f"写入 Excel 文件 '{output_path}' 时出错: {e}") from e


def write_to_srt(data, output_path):
    """
    将提取的数据写入一个 .srt 文件。
    :param data: 包含所有字幕信息的二维列表。格式: [序号, 开始时间, 结束时间, 字幕内容]
    :param output_path: 输出的 .srt 文件的完整路径。
    :raises WriteError: 当写入过程出错时。
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for i, entry in enumerate(data):
                index, start_time, end_time, text = entry
                # SRT格式要求：序号、时间码、文本、空行
                f.write(f"{index}\n")
                f.write(f"{start_time} --> {end_time}\n")
                f.write(f"{text}\n")
                f.write("\n") # 块之间的空行
    except Exception as e:
        raise WriteError(f"写入 SRT 文件 '{output_path}' 时出错: {e}") from e