
import re
import requests
import json
import pandas as pd
from collections import defaultdict
import os

def get_root_path():
    """
    获取ODCSOFT_KINGLONG的根路径
    """
    current_path = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件的绝对路径
    root_path = os.path.dirname(os.path.dirname(current_path))  # 向上回溯一层到根目录
    return root_path

def loadODCboundary():
    #导入ODC边界,保存边界值,返回10类元素，每一类下面又有子级别
    root_path = get_root_path()
    file_path = os.path.join(root_path, "monitorODC\\ODC边界检查表.xlsx")
    sheet_name = 'Sheet1'
    # 读取 Excel 数据
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    # 填充空值
    df['一级分类'] = df['一级分类'].fillna(method='ffill')
    df['二级分类'] = df['二级分类'].fillna(method='ffill')
    df['三级分类'] = df['三级分类'].fillna("")

    # 处理边界值的函数
    def process_value(value):
        if isinstance(value, str):
            value = value.strip()  # 去掉首尾空格
            if value.lower() == 'true':
                return True
            elif value.lower() == 'false':
                return False
            # 匹配括号中的内容（支持中英文括号）
            match = re.match(r'^[\(\（](.*?)[\)\）]$', value)
            if match:
                return tuple(v.strip().strip("'") for v in match.group(1).split(','))
            # 匹配范围值
            elif value.startswith('[') and value.endswith(']'):
                try:
                    range_values = [float(v.strip()) for v in value[1:-1].split(',')]
                    return range_values
                except ValueError:
                    pass  # 如果转换失败，返回原始值
        return value  # 其他情况返回原始值

    # 应用边界值处理
    df['value'] = df['边界值（只允许的状态）'].apply(process_value)

    # 创建嵌套字典结构
    nested_data = defaultdict(lambda: defaultdict(dict))

    for _, row in df.iterrows():
        # 一级分类 -> 二级分类 -> 三级分类和对应值
        nested_data[row['一级分类']][row['二级分类']][row['三级分类']] = {"value": row['value']}

    # 转换为标准字典
    nested_data = dict(nested_data)

    # 转换为 JSON 数据
    json_data = json.dumps(nested_data, ensure_ascii=False, indent=4)

    # 输出结果
    nested_dict = json.loads(json_data)
    return nested_dict

ODC = loadODCboundary()