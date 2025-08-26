import os
import json
import time
import datetime
import requests
import heapq
import numpy as np
from flask import Flask, request, jsonify
from scipy.optimize import minimize
import shutil
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from apscheduler.executors.pool import ThreadPoolExecutor
import threading
import copy
import riskassessment.risk_assessment as rs
import riskassessment.ODCboundary as rodcb


lock=threading.Lock()
app = Flask(__name__)

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
# api_endpoints = {
#     "map_local_state": "http://0.0.0.0:5008/get_map_local_state",
#     "driver_state": "http://0.0.0.0:5008/get_driver_state",
#     "vehicle_state": "http://0.0.0.0:5008/get_vehicle_state",
#     "communica_condi_state": "http://0.0.0.0:5008/get_communica_condi_state",
#     "tran_condi_state": "http://0.0.0.0:5008/get_tran_condi_state",
#     "digital_state": "http://0.0.0.0:5008/get_digtal_state",
#     "road_infrustrction_state": "http://0.0.0.0:5008/get_road_infrucstrcution_state",
#     "weather_state": "http://0.0.0.0:5008/get_weather_state",
#     "road_information_state": "http://0.0.0.0:5008/get_road_information_state",
#     "object_state": "http://0.0.0.0:5008/get_object_state",
# }

# 每个API的参数
api_params = {
    "map_local_state": {  # 地图和定位状态，变化较慢(除非高速移动)
        "alpha": 1.0,    # 高重要性
        "beta": 0.15,    # 中等动态性
        "c_i": 0.024,
        "tau": 0.1,
        "B_i": 10.0,
        "s_i": 8.0
    },
    "driver_state": {    # 驾驶员状态(注意力、疲劳等)，变化中等
        "alpha": 0.8,
        "beta": 0.56,    # 较高动态性(驾驶员状态可能快速变化)
        "c_i": 0.021,
        "tau": 0.1,
        "B_i": 20.0,
        "s_i": 15.0
    },
    "vehicle_state": {   # 车辆状态(速度、加速度等)，高速时变化快
        "alpha": 0.6,
        "beta": 0.3,     # 高动态性(特别是加速/制动时)
        "c_i": 0.031,
        "tau": 0.05,
        "B_i": 30.0,
        "s_i": 25.0
    },
    "communica_condi_state": {  # 通信条件，通常较稳定
        "alpha": 0.5,
        "beta": 0.1,     # 低动态性(除非进出隧道等)
        "c_i": 0.023,
        "tau": 0.1,
        "B_i": 40.0,
        "s_i": 39.0
    },
    "tran_condi_state": {  # 交通条件，取决于交通流密度
        "alpha": 0.7,
        "beta": 0.2,     # 中等动态性
        "c_i": 0.016,
        "tau": 1,
        "B_i": 25.0,
        "s_i": 20.0
    },
    "digital_state": {   # 数字系统状态，通常较稳定
        "alpha": 0.4,
        "beta": 0.15,    # 低动态性
        "c_i": 0.015,
        "tau": 1,
        "B_i": 50.0,
        "s_i": 45.0
    },
    "road_infrustrction_state": {  # 道路设施状态，通常稳定
        "alpha": 0.9,    # 高重要性(如交通标志)
        "beta": 0.13,    # 低动态性
        "c_i": 0.024,
        "tau": 1,
        "B_i": 15.0,
        "s_i": 12.0
    },
    "weather_state": {   # 天气状态，通常变化缓慢
        "alpha": 0.3,
        "beta": 0.05,    # 极低动态性
        "c_i": 0.027,
        "tau": 1,
        "B_i": 60.0,
        "s_i": 55.0
    },
    "road_information_state": {  # 道路信息(如拥堵)，中等变化
        "alpha": 0.5,
        "beta": 0.18,    # 中等偏低动态性
        "c_i": 0.035,
        "tau": 1,
        "B_i": 35.0,
        "s_i": 30.0
    },
    "object_state": {    # 周围物体状态，高速时变化极快
        "alpha": 1.0,
        "beta": 0.8,     # 极高动态性(特别是近距离物体)
        "c_i": 0.023,
        "tau": 0.03,
        "B_i": 20.0,
        "s_i": 10.0
    }
}
# 资源约束
C_max = 1  # 系统允许的最大计算资源
# 风险变量
risk_all = {
    "timestamp":None,
    "data":None
}

all_api_data = {}
and_result = None

def get_current_file_path():
    """
    生成当前 5 分钟的文件路径，例如：
    E:\monitorODC\ODCelement\oddtimestamp_2025-03-25_14-35.json
    """
    timestamp = datetime.now()
    minute_group = (timestamp.second // 5) * 5  # 按秒进行上传
    file_name = f"oddtimestamp_{timestamp.strftime('%Y-%m-%d_%H')}-{minute_group}.json"
    return os.path.join(output_dir, file_name)

def get_json_file_path(directory_path, recursive=False):
    # 校验路径有效性
    if not os.path.isdir(directory_path):
        raise NotADirectoryError(f"提供的路径 '{directory_path}' 不存在或不是文件夹")
    
    # 定义不同遍历模式的文件收集方式
    def scan_files():
        if recursive:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    if file.endswith('.json'):
                        yield os.path.join(root, file)
        else:
            for file in os.listdir(directory_path):
                full_path = os.path.join(directory_path, file)
                if os.path.isfile(full_path) and file.endswith('.json'):
                    yield full_path
    
    # 执行扫描并返回排序结果
    return sorted(scan_files(), key=lambda x: (not os.path.basename(x).startswith('config'), x))

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

def save_and_result(file_path, timestamp, and_result, all_api_data, risk_data):
    """
    保存 API 数据到 JSON 文件
    """
    try:
        existing_data = {}
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        # 追加新数据
        existing_data[timestamp] = copy.deepcopy(all_api_data)
        existing_data[timestamp]["and_result"] = and_result
        existing_data[timestamp]["TTC"] = risk_data["TTC"]
        existing_data[timestamp]["driving_mode"] = risk_data["driving_mode"]
        existing_data[timestamp]["driving_risk"] = risk_data["driving_risk"]
        existing_data[timestamp]["num_level"] = risk_data["num_level"]
        existing_data[timestamp]["str_level"] = risk_data["str_level"]
        existing_data[timestamp]["system_risk"] = risk_data["system_risk"]
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
        print(f"数据已保存到 {file_path}，时间戳：{timestamp}")
    except Exception as e:
        print(f"发生错误：{e}")

def fetch_api_data(api_name):
    """
    获取单个 API 数据
    """
    global and_result, all_api_data
    api_url = api_endpoints[api_name]
    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()  # 检查请求是否成功
        data = response.json()
        if len(data) < 3:
            print(f"数据格式异常：{data}")
            return
        data_1 = data[1]
        with lock:
            if and_result is None:
                and_result = data_1
            else:
                and_result &= data_1
            all_api_data[api_name] = {"detailed_info": data, "and_result": data_1}
            all_api_data['update_time']=time.time()
    except requests.exceptions.RequestException as e:
        print(f"接口 {api_name} 请求错误：{e}")
    except json.JSONDecodeError as e:
        print(f"接口 {api_name} 数据解析错误：{e}")

# def fetch_risk_api_data():
#     """
#     获取风险数据
#     """
#     url = "http://127.0.0.1:5010/risk_value"
#     try:
#         response = requests.get(url, timeout=5)
#         response.raise_for_status()  # 检查请求是否成功
#         data = response.json()
#         return data
#     except requests.exceptions.RequestException as e:
#         print(f"请求错误：{e}")
#         return {"TTC": 0, "driving_mode": 0, "driving_risk": 0, "num_level": 0, "str_level": "normal", "system_risk": 0}
#     except json.JSONDecodeError as e:
#         print(f"数据解析错误：{e}")
#         return {"TTC": 0, "driving_mode": 0, "driving_risk": 0, "num_level": 0, "str_level": "normal", "system_risk": 0}

def calculate_dynamic_factor(api_info):
    """
    计算动态调整因子
    """
    delta_i = abs(api_info["B_i"] - api_info["s_i"])
    delta_i_max = api_info["B_i"]  # 假设最大边界差值为B_i
    return 1 - (delta_i / delta_i_max)

def optimize_monitoring_frequencies():
    """
    优化监测频率
    """

    alphas = np.array([api_info["alpha"] for api_info in api_params.values()])
    betas = np.array([api_info["beta"] for api_info in api_params.values()])
    c_i = np.array([api_info["c_i"] for api_info in api_params.values()])
    taus = np.array([api_info["tau"] for api_info in api_params.values()])
    B_i = np.array([api_info["B_i"] for api_info in api_params.values()])
    s_i = np.array([api_info["s_i"] for api_info in api_params.values()])

    # 计算动态调整因子
    gamma_i = np.array([calculate_dynamic_factor(api_info) for api_info in api_params.values()])

    # 定义优化目标函数
    def objective(frequencies):
        benefit = np.sum(gamma_i * alphas * (1 - np.exp(-frequencies / (betas + 1e-6))))
        return -benefit

    # 定义约束条件
    constraints = [
        {'type': 'ineq', 'fun': lambda frequencies: C_max - np.sum(c_i * frequencies)},  # 资源约束
    ]

    # 添加频率上下限约束
    for i, tau in enumerate(taus):
        constraints.append({'type': 'ineq', 'fun': lambda frequencies, i=i: frequencies[i] - 0.1})  # 最小0.1Hz
        constraints.append(
            {'type': 'ineq', 'fun': lambda frequencies, i=i, tau=tau: 1.0 / tau - frequencies[i]})  # 最大1/tau

    # 初始猜测值 - 平均分配资源
    initial_guess = np.ones(len(taus)) * (C_max / np.sum(c_i))

    # 优化 - 使用SLSQP方法
    result = minimize(objective, initial_guess, method='SLSQP',
                      constraints=constraints)

    if not result.success:
        print("优化失败:", result.message)
        optimal_frequencies = initial_guess * (C_max / np.sum(c_i * initial_guess))
    else:
        optimal_frequencies = result.x

    # 更新监测频率
    for i, (api_name, api_info) in enumerate(api_params.items()):
        api_info["interval"] = 1.0 / optimal_frequencies[i]
        print(f"{api_name}: {optimal_frequencies[i]:.2f}Hz (间隔:{api_info['interval']:.2f}s)")

    # 打印总资源使用情况
    total_resource = np.sum(c_i * optimal_frequencies)
    print(f"总资源使用: {total_resource:.2f}/{C_max}")

def update_monitoring_frequencies():
    """
    定期更新监测频率
    """
    optimize_monitoring_frequencies()
    reschedule_jobs()
    print("监测频率已更新")

def reschedule_jobs():
    """
    根据新的频率重新安排所有任务
    """
    scheduler.remove_all_jobs()
    for api_name, api_info in api_params.items():
        interval = api_info["interval"]
        scheduler.add_job(lambda name=api_name: fetch_api_data(name), 'interval', seconds=interval,max_instances=100)

@app.route("/risk_value")
def get_system_risk():
    global all_api_data, risk_all
    try:
        if not all_api_data:
            print('all_api_data尚未有数据存入')
            return jsonify({"status": "error", "message": "数据未初始化"}), 404
        else:
            return jsonify({
                "status": "success",
                "timestamp": risk_all["timestamp"],
                "system_risk": risk_all["data"]["system_risk"],
                "risk_details": risk_all["data"]["risk_details"],
                "TTC": risk_all["data"]["TTC"],
                "driving_risk": risk_all["data"]["driving_risk"],
                "driving_mode": risk_all["data"]["driving_mode"],
                "num_level": risk_all["data"]["num_level"],
                "str_level": risk_all["data"]["str_level"]
            }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/collect_and_save", methods=["POST"])
def collect_and_save():
    global all_api_data
    global risk_all
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            risk, tenrisklist, driving_risk, TTC, num_level, str_level, driving_mode = rs.risk_cal(all_api_data, rodcb.all_odc_boundary, rodcb.KEY_INDEX_MAP, rodcb.w_map)
        except Exception as e:
            print(f"错误{e}")
        risk_all = {
            "timestamp": timestamp,
            "data":{
                "system_risk": risk,
                "risk_details": tenrisklist,
                "TTC":TTC,
                "driving_risk": driving_risk,
                "driving_mode": driving_mode,
                "num_level": num_level,
                "str_level": str_level
            }
        }
        #risk_data = fetch_risk_api_data()
        # 获取当前 5 分钟的文件路径
        file_path = get_current_file_path()
        # 保存数据
        save_and_result(file_path, timestamp, and_result, all_api_data, risk_all['data'])
        # 删除旧文件
        delete_old_files()

        return jsonify({"status": "success", "timestamp": timestamp}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# @app.route("/get_results", methods=["GET"])
# def get_results():
#     global and_result
#     try:
#         start = request.args.get("start")
#         end = request.args.get("end")

#         # 获取当前的 JSON 文件
#         file_path = get_json_file_path(output_dir)[0]

#         if not os.path.exists(file_path):
#             return jsonify({"status": "error", "message": "数据文件不存在"}), 404

#         with open(file_path, "r", encoding="utf-8") as f:
#             data = json.load(f)

#         if start and end:
#             try:
#                 start_time = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
#                 end_time = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
#             except ValueError:
#                 return jsonify({"status": "error", "message": "时间格式错误"}), 400

#             filtered_data = {
#                 timestamp: entry
#                 for timestamp, entry in data.items()
#                 if start_time <= datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S") <= end_time
#             }
#         else:
#             filtered_data = data
#         and_result=None
#         return jsonify(filtered_data), 200
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/get_results", methods=["GET"])
def get_results():
    """
    根据时间范围查询数据
    """
    try:
        files = os.listdir(output_dir)

        # 过滤出 JSON 文件
        json_files = [file for file in files if file.endswith('.json')]

        # 如果没有找到 JSON 文件，退出程序
        if not json_files:
            print("未找到任何 JSON 文件。")
            exit()

        # 如果只有一个 JSON 文件，直接获取该文件
        if len(json_files) == 1:
            json_file = json_files[0]
        else:
            print("文件夹中有多个 JSON 文件，请检查。")
            exit()

        # 构造完整的文件路径
        file_path = os.path.join(output_dir, json_file)

        # 从文件中加载 JSON 数据
        with open(file_path, 'r', encoding='utf-8') as file:
            json_data = json.load(file)

        # 将时间戳字符串转换为 datetime 对象，并找到最新的时间戳
        latest_timestamp = max(json_data.keys(), key=lambda k: datetime.strptime(k, "%Y-%m-%d %H:%M:%S"))

        # 获取最新时间点的信息
        latest_info = json_data[latest_timestamp]

        # 将最新时间点的信息包装为字典
        latest_info_dict = {latest_timestamp: latest_info}
        return jsonify(latest_info_dict),200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    # 初始化调度器
    executors = {
        'default': ThreadPoolExecutor(160)  # 增加线程池大小到 50
    }
    scheduler = BackgroundScheduler(executors=executors)
    # 启动定时任务，每5秒更新一次监测频率
    now=datetime.now()
    scheduler.add_job(update_monitoring_frequencies, 'interval',seconds=60,max_instances=1, replace_existing=True,next_run_time=now)
    scheduler.start()
    # 启动Flask应用
    app.run(host="0.0.0.0", port=5009, debug=True)
    # app.run(host="127.0.0.1", port=5009, debug=True)
    os.makedirs(output_dir, exist_ok=True)


