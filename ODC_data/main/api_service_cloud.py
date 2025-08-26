from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

# 设置文件路径
def get_root_path():
    """
    获取ODCSOFT_KINGLONG的根路径
    """
    current_path = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件的绝对路径
    root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))  # 向上回溯三层到根目录
    return root_path

# 使用相对路径构建完整路径
root_path = get_root_path()
file_path = os.path.join(root_path, "monitorODC\\ODC_data\\data-real-time\\cloud.json")


def read_and_parse_file():
    if not os.path.exists(file_path):
        return {"error": "文件未找到"}

    try:
        # 读取原始 JSON 数据
        with open(file_path, 'r', encoding='utf-8') as file:
            raw_data = json.load(file)

        # 解析数据并提取所需内容
        decoded_data = []

        # 假设原始数据是类似于你提供的结构
        if 'data' in raw_data and 'rsis' in raw_data['data']:
            for event in raw_data['data']['rsis']:
                # 获取 content 并将其从字符串转换为字典
                content_str = event.get('content', '{}')  # 获取 content 字段
                try:
                    content = json.loads(content_str)  # 将字符串解析为字典
                except json.JSONDecodeError:
                    content = {}  # 如果解析失败，则返回空字典

                # 获取 advSpd 数组中的第一个元素
                adv_spd = content.get('advSpd', [{}])[0]  # 默认取第一个元素，如果为空，则为一个空字典
                event_position = event.get('eventPosition', {})

                # 检查字段数据
                print(f"[Debug] content data: {content}")
                print(f"[Debug] advSpd data: {adv_spd}")

                # 检查 d2StopLine 是否在 content 中
                d2StopLine = content.get('d2StopLine', '未知')  # 获取与停止线的距离
                print(f"[Debug] d2StopLine: {d2StopLine}")  # 打印 d2StopLine 数据

                event_data = {
                    "车辆ID": raw_data['data'].get('vehicleId', '未知'),
                    "事件ID": event.get("uuid", ""),
                    "事件类型": f"{event.get('eventType', '未知')}（待定义）",
                    "事件优先级": f"{event.get('priority', '未知')}（最低优先级）",
                    "事件来源": f"{event.get('eventSource', '未知')}（待定义）",
                    "预计速度": f"{adv_spd.get('spdExp', '未知')} km/h" if isinstance(adv_spd, dict) else '未知',
                    "最大速度": f"{adv_spd.get('spdMax', '未知')} km/h" if isinstance(adv_spd, dict) else '未知',
                    "最小速度": f"{adv_spd.get('spdMin', '未知')} km/h" if isinstance(adv_spd, dict) else '未知',
                    "交叉口数量": f"{adv_spd.get('numIntersection', '未知')}" if isinstance(adv_spd, dict) else '未知',
                    "行为类型": f"{adv_spd.get('maneuver', '未知')}（待定义）" if isinstance(adv_spd, dict) else '未知',
                    "与停止线的距离": f"{d2StopLine}米",  # 显示与停止线的距离
                    "事件位置": {
                        "纬度": event_position.get("latitude", '未知') if isinstance(event_position, dict) else '未知',
                        "经度": event_position.get("longitude", '未知') if isinstance(event_position, dict) else '未知',
                        "海拔": event_position.get("elevation", '未知') if isinstance(event_position, dict) else '未知'
                    },
                    "事件发生时间戳": event.get("timestamp", '未知'),
                    "UUID": event.get("uuid", "未知")
                }
                decoded_data.append(event_data)

        return decoded_data

    except json.JSONDecodeError:
        return {"error": "JSON 文件解析失败"}
    except Exception as e:
        return {"error": f"发生错误: {str(e)}"}




# API 路由：返回解析后的 CAN 数据
@app.route('/get_event_info', methods=['GET'])
def get_event_info():
    """
    获取解析后的事件信息
    :return: JSON 格式的解析结果
    """
    print("[Info] API /get_event_info called")
    parsed_data = read_and_parse_file()
    if "error" in parsed_data:
        return jsonify(parsed_data), 500
    return jsonify(parsed_data), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5004, debug=True)
