import os
import json
import time
import datetime
import requests
from flask import Flask, request, jsonify, Response
import shutil
import riskassessment.risk_assessment as rs
import riskassessment.ODCboundary as rodcb

app = Flask(__name__)

# 全局变量，存储最新数据
latest_api_data = {
    "timestamp": None,
    "and_result": None,
    "all_api_data": None,
    "risk_data": None,  # 存储计算后的风险结果
    "posx": 30,
    "posx": 5,
    "posx": 6,
    "posx": 2
}

def get_root_path():
    """
    获取ODCSOFT_KINGLONG的根路径
    """
    current_path = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件的绝对路径
    root_path = os.path.dirname(current_path) # 向上回溯一层到根目录
    return root_path

# 存储文件的目录
root_path = get_root_path()
output_dir = os.path.join(root_path, "monitorODC\\ODCelement")
output_dir1 = os.path.join(root_path, "monitorODC\\send2cloud")

# API 地址定义
api_endpoints = {
    "map_local_state": "http://127.0.0.1:5008/get_map_local_state",
    "driver_state": "http://127.0.0.1:5008/get_driver_state",
    "vehicle_state": "http://127.0.0.1:5008/get_vehicle_state",
    "communica_condi_state": "http://127.0.0.1:5008/get_communica_condi_state",
    "tran_condi_state": "http://127.0.0.1:5008/get_tran_condi_state",
    "digital_state": "http://127.0.0.1:5008/get_digtal_state",
    "road_infrustrction_state": "http://127.0.0.1:5008/get_road_infrucstrcution_state",
    "weather_state": "http://127.0.0.1:5008/get_weather_state",
    "road_information_state": "http://127.0.0.1:5008/get_road_information_state",
    "object_state": "http://127.0.0.1:5008/get_object_state",
}
def get_current_file_path():
    """
    生成当前 5 分钟的文件路径，例如：
    E:\monitorODC\ODCelement\oddtimestamp_2025-03-25_14-35.json
    """
    timestamp = datetime.datetime.now()
    # 此处修改上传云端时间间隔
    # minute_group = (timestamp.minute // 1) * 1  # 按分钟进行上传
    minute_group = (timestamp.second // 5) * 5  # 按秒进行上传
    file_name = f"oddtimestamp_{timestamp.strftime('%Y-%m-%d_%H')}-{minute_group}.json"
    return os.path.join(output_dir, file_name)

def delete_old_files():
    """
    删除 output_dir 目录下的旧 JSON 文件，仅保留最新的 1 个文件。
    """
    files = [f for f in os.listdir(output_dir) if f.startswith("oddtimestamp_") and f.endswith(".json")]
    files.sort(reverse=True)  # 按文件名排序，最新的文件在前

    if len(files) > 1:
        for old_file in files[1:]:  # 保留最新的，删除其他的
            shutil.copy(os.path.join(output_dir, old_file), os.path.join(output_dir1, "lasted.json"))
            print(f"已复制旧文件: {old_file}到新文件{'lasted.json'}")
            os.remove(os.path.join(output_dir, old_file))
            print(f"已删除旧文件: {old_file}")

def save_and_result(file_path, timestamp, and_result, all_api_data,risk_data):
    """
    保存 API 数据到 JSON 文件
    """
    try:
        existing_data = {}
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        # 追加新数据
        existing_data[timestamp] = all_api_data
        existing_data[timestamp]["and_result"] = and_result
        existing_data[timestamp]["TTC"]=risk_data["TTC"]
        existing_data[timestamp]["driving_mode"]=risk_data["driving_mode"]
        existing_data[timestamp]["driving_risk"]=risk_data["driving_risk"]
        existing_data[timestamp]["num_level"]=risk_data["num_level"]
        existing_data[timestamp]["str_level"]=risk_data["str_level"]
        existing_data[timestamp]["system_risk"]=risk_data["system_risk"]
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
        print(f"数据已保存到 {file_path}，时间戳：{timestamp}")
    except Exception as e:
        print(f"发生错误：{e}")


def fetch_api_data():
    """
    获取所有 API 数据
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    and_result = None
    all_api_data = {}

    for api_name, api_url in api_endpoints.items():
        try:
            response = requests.get(api_url)
            response.raise_for_status()  # 检查请求是否成功
            data = response.json()

            if len(data) < 3:
                print(f"数据格式异常：{data}")
                continue

            data_1 = data[1]

            if and_result is None:
                and_result = data_1
            else:
                and_result &= data_1

            all_api_data[api_name] = {"detailed_info": data, "and_result": data_1}

        except requests.exceptions.RequestException as e:
            print(f"接口 {api_name} 请求错误：{e}")
        except json.JSONDecodeError as e:
            print(f"接口 {api_name} 数据解析错误：{e}")

    return timestamp, and_result, all_api_data

# def fetch_risk_api_data():
#     """
#     获取所有 API 数据
#     """
#     all_api_data = {}
#     url = 'http://127.0.0.1:5010/risk_value'
#     try:
#         response = requests.get(url)
#         response.raise_for_status()  # 检查请求是否成功
#         data = response.json()

#     except requests.exceptions.RequestException as e:
#         print(f"请求错误：{e}")
#     except json.JSONDecodeError as e:
#         print(f"数据解析错误：{e}")

#     return data

@app.route("/collect_and_save", methods=["POST"])
def collect_and_save():
    global latest_api_data
    try:
        timestamp, and_result, all_api_data = fetch_api_data()
        print(all_api_data)
        risk, tenrisklist, driving_risk, TTC, num_level, str_level, driving_mode = rs.risk_cal(all_api_data, rodcb.all_odc_boundary, rodcb.KEY_INDEX_MAP, rodcb.w_map)
        # 在此处风险代码输入为all_api_data，但是仍然保留输出的接口
        latest_api_data = {
            "timestamp": timestamp,
            "and_result": and_result,
            "all_api_data": all_api_data,
            "risk_data": {
                "timestamp": timestamp,
                "system_risk": risk,
                "risk_details": tenrisklist,
                "TTC":TTC,
                "driving_risk": driving_risk,
                "driving_mode": driving_mode,
                "num_level": num_level,
                "str_level": str_level
            }
        }
        risk_data=latest_api_data["risk_data"]
        # 获取当前 5 分钟的文件路径
        file_path = get_current_file_path()

        # 保存数据
        save_and_result(file_path, timestamp, and_result, all_api_data,risk_data)
        print(file_path, timestamp, and_result,risk_data)
        # 删除旧文件
        delete_old_files()

        return jsonify({"status": "success", "timestamp": timestamp}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/get_results", methods=["GET"])
def get_results():
    """
    根据时间范围查询数据
    """
    try:
        start = request.args.get("start")
        end = request.args.get("end")

        # 获取当前的 JSON 文件
        file_path = get_current_file_path()

        if not os.path.exists(file_path):
            return jsonify({"status": "error", "message": "数据文件不存在"}), 404

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if start and end:
            try:
                start_time = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
                end_time = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return jsonify({"status": "error", "message": "时间格式错误"}), 400

            filtered_data = {
                timestamp: entry
                for timestamp, entry in data.items()
                if start_time <= datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") <= end_time
            }
        else:
            filtered_data = data

        return jsonify(filtered_data), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/risk_value", methods=["GET"])
def get_system_risk():
    try:
        if not latest_api_data["timestamp"]:
            return jsonify({"status": "error", "message": "数据未初始化"}), 404
            
        return jsonify({
            "status": "success",
            "timestamp": latest_api_data["timestamp"],
            "system_risk": latest_api_data["risk_data"]["system_risk"],
            "risk_details": latest_api_data["risk_data"]["risk_details"],
            "TTC": latest_api_data["risk_data"]["TTC"],
            "driving_risk": latest_api_data["risk_data"]["driving_risk"],
            "driving_mode": latest_api_data["risk_data"]["driving_mode"],
            "num_level": latest_api_data["risk_data"]["num_level"],
            "str_level": latest_api_data["risk_data"]["str_level"]
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/video_feed', methods=["GET"])
def video_feed():
    print("Received /video_feed request")
    return Response(rs.generate_video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5009, debug=True)
    os.makedirs(output_dir, exist_ok=True)

