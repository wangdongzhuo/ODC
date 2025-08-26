import requests
import json
import os
import datetime
import time

def save_and_result(file_path, timestamp, and_result, all_api_data):
    """
    保存所有接口的 data[1] 运算后的结果到指定文件中，并存储所有 API 的详细信息。
    
    :param file_path: 本地文件保存路径
    :param timestamp: 固定的时间戳
    :param and_result: 与运算的结果
    :param all_api_data: 包含所有 API 详细信息的字典
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        else:
            existing_data = {}

        # 存入所有接口的详细信息
        existing_data[timestamp] = all_api_data
        existing_data[timestamp]["and_result"] = and_result

        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 保存数据
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)

        print(f"数据已保存到 {file_path}，时间戳：{timestamp}")
    except Exception as e:
        print(f"发生错误：{e}")

# 定义多个接口及其保存的键名
api_endpoints = {
    "map_local_state": "http://127.0.0.1:5008/get_map_local_state",
    # "vehicle_state": "http://127.0.0.1:5008/get_vehicle_state",   #vehicle 这一条有问题，有些数据没有，2025/02/26/16：20
    # "driver_state": "http://127.0.0.1:5008/get_driver_state",     #driver 这一条也要修改一下，想想怎么描述
    "communica_condi_state": "http://127.0.0.1:5008/get_communica_condi_state",
    "tran_condi_state": "http://127.0.0.1:5008/get_tran_condi_state",
    "digital_state": "http://127.0.0.1:5008/get_digtal_state",
    "road_infrustrction_state": "http://127.0.0.1:5008/get_road_infrucstrcution_state", 
    "weather_state": "http://127.0.0.1:5008/get_weather_state",#运行weather_state的时候不能连接vpn
    "road_information_state": "http://127.0.0.1:5008/get_road_information_state",
    "object_state": "http://127.0.0.1:5008/get_object_state",      
}

# 指定保存数据的文件路径
output_file_path = r"E:\monitorODC\ODCelement\oddtimestamp.json"


while True:
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    and_result = None
    all_api_data = {}

    for api_name, api_url in api_endpoints.items():
        try:
            response = requests.get(api_url)
            data = response.json()

            if len(data) < 3:
                print(f"数据格式异常：{data}")
                continue

            data_1 = data[1]

            if and_result is None:
                and_result = data_1
            else:
                and_result &= data_1

            # 存储每个接口的详细数据
            all_api_data[api_name] = {"detailed_info": data, "and_result": data_1}

        except Exception as e:
            print(f"接口 {api_name} 请求错误：{e}")

    save_and_result(output_file_path, timestamp, and_result, all_api_data)
    time.sleep(1)

