from flask import Flask, jsonify
from parsers.rules_mapping import get_parser
import os
import json

# ... existing code ...

# 获取ODCSOFT_KINGLONG根路径
def get_root_path():
    """
    获取ODCSOFT_KINGLONG的根路径
    """
    current_path = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件的绝对路径
    root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))  # 向上回溯三层到根目录
    return root_path

# 使用相对路径构建完整路径
root_path = get_root_path()
file_path = os.path.join(root_path, "monitorODC\\ODC_data\\data-real-time\\香港车ECAN.txt")
app = Flask(__name__)
last_read_position = 0  # 上次读取文件的位置
no_data_logged = False  # 控制日志输出的全局标志位

#修改此处的字典
all_categories = {
    "控制转向系统报文": {"timestamp": 0, "data": {}},
    "控制驱动和制动系统报文": {"timestamp": 0, "data": {}},
    "状态反馈和状态请求报文": {"timestamp": 0, "data": {}},
    "状态反馈和状态请求报文2": {"timestamp": 0, "data": {}},
    "协同控制器系统故障报文": {"timestamp": 0, "data": {}},
    "AS控制L2系统报文": {"timestamp": 0, "data": {}},
    "驱动状态报文": {"timestamp": 0, "data": {}},
    "域控制器基础信息1": {"timestamp": 0, "data": {}},
    "域控制器基础信息2": {"timestamp": 0, "data": {}},
    "高压电池状态报文": {"timestamp": 0, "data": {}},
    "域控制器基础信息": {"timestamp": 0, "data": {}},
    "转向系统状态反馈": {"timestamp": 0, "data": {}},
    "L2功能状态反馈": {"timestamp": 0, "data": {}},
    "智能控制状态反馈": {"timestamp": 0, "data": {}},
    "智能车辆状态反馈": {"timestamp": 0, "data": {}},
    "车辆车速报文": {"timestamp": 0, "data": {}},
    "轮速报文": {"timestamp": 0, "data": {}},
    "胎压监控系统状态": {"timestamp": 0, "data": {}},
    "车辆加速度信息": {"timestamp": 0, "data": {}},
    "主目标信息": {"timestamp": 0, "data": {}},
    "车辆里程总报文": {"timestamp": 0, "data": {}},
    "左车道线状态1": {"timestamp": 0, "data": {}},
    "左车道线状态2": {"timestamp": 0, "data": {}},
    "右车道线状态1": {"timestamp": 0, "data": {}},
    "右车道线状态2": {"timestamp": 0, "data": {}}
}

# 解析文件中的新数据
def read_new_lines():
    """
    读取文件中新增的行并解析
    :return: 包含解析结果的完整字典
    """
    global last_read_position, all_categories

    # 检查文件路径是否存在
    if not os.path.exists(file_path):
        print(f"[Error] File does not exist: {file_path}")
        return all_categories  # 直接返回初始化的类别数据

    try:
        # 打开文件读取新增的行
        with open(file_path, "r") as file:
            file.seek(last_read_position)  # 从上次读取的位置开始
            lines = file.readlines()  # 读取新增的所有行
            last_read_position = file.tell()  # 更新读取位置
            print(f"[Debug] Read {len(lines)} new lines from file.")
    except Exception as e:
        print(f"[Error] Unable to read file: {e}")
        return all_categories  # 返回完整的初始化类别

    # 如果没有新行，直接返回   修改代码加入判断，每隔0.05s判断一次有没有新行写入
    if not lines:
        print("[Info] No new lines found.")
        return all_categories

    # 解析每一行数据
    for line in lines:
        #print(f"[Info] Processing line: {line.strip()}")
        parts = line.strip().split()
        if len(parts) < 6:
            print(f"[Warning] Ignored incomplete line: {line.strip()}")
            continue

        # 提取数据字段
        try:
            timestamp = float(parts[0])  # 时间戳
            can_id = parts[2].rstrip('x')  # CAN ID
            raw_data = " ".join(parts[6:])  # 数据内容
        except Exception as e:
            print(f"[Error] Failed to extract data from line: {e}")
            continue

        # 根据 CAN ID 获取解析器并解析数据
        try:
            parser_class = get_parser(can_id)
            #print(f"[Info] Using parser class: {parser_class.__name__}")
            parser_instance = parser_class(raw_data)
            parsed_fields = parser_instance.parse()
        except Exception as e:
            print(f"[Error] Parsing failed for CAN ID {can_id}: {e}")
            parsed_fields = {}

        # 更新 all_categories 的内容
        for category, content in parsed_fields.items():
            if category in all_categories:
                existing_data = all_categories[category]
                if "timestamp" not in existing_data or timestamp > existing_data["timestamp"]:
                    # print(f"[Update] Updating category '{category}' with new timestamp {timestamp}. Previous timestamp: {existing_data.get('timestamp', 0)}")
                    all_categories[category] = {"timestamp": timestamp, "data": content}
                else:
                    # print(f"[Skip] Skipping category '{category}' as existing timestamp {existing_data.get('timestamp', 0)} is newer.")
                    pass
            else:
                print(f"[New] Adding new category '{category}' with timestamp {timestamp}")
                all_categories[category] = {"timestamp": timestamp, "data": content}

    # 返回完整的所有类别数据
    return all_categories

# API 路由：返回新增的 CAN 数据
@app.route('/get_can_data', methods=['GET'])
def get_can_data():
    """
    获取所有类别的 CAN 数据（带初始值）
    :return: JSON 格式的解析结果
    """
    global no_data_logged  # 使用全局标志位
    print("[Info] API /get_can_data called")
    new_data = read_new_lines()
    if not new_data:
        if not no_data_logged:  # 如果之前没有提示过
            print("[Info] No new data available.")
            no_data_logged = True  # 设置标志位为 True
        return jsonify([]), 204
    no_data_logged = False  # 有新数据时重置标志位
    return jsonify(new_data), 200

# 主程序入口
if __name__ == '__main__':
    print(f"[Info] Starting API service with file: {file_path}")
    app.run(host='127.0.0.1', port=5001, debug=True)
