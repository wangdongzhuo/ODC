import requests
import time
from enum import Enum
from flask import Flask, jsonify  # 新增Flask依赖

app = Flask(__name__)  # 新增Flask应用实例

# 使用了 requests 库来发起HTTP请求，使用 time 库来控制请求的频率
# 接口URL
url   = "http://127.0.0.1:5010/risk_value"
url1  = "http://127.0.0.1:5008/get_object_state"
url2  = "http://127.0.0.1:5008/get_road_information_state"
url3  = "http://127.0.0.1:5008/get_weather_state"
url4  = "http://127.0.0.1:5008/get_road_infrucstrcution_state"
url5  = "http://127.0.0.1:5008/get_digtal_state"
url6  = "http://127.0.0.1:5008/get_tran_condi_state"
url7  = "http://127.0.0.1:5008/get_communica_condi_state"
url8  = "http://127.0.0.1:5008/get_driver_state"
url9  = "http://127.0.0.1:5008/get_vehicle_state"
url10 = "http://127.0.0.1:5008/get_map_local_state"

#################### 驾驶模式枚举 ####################
class DrivingMode(Enum):
    AD = "autonomous_mode"  # 自动驾驶模式
    DG = "degraded_mode"    # 降级模式
    TD = "takeover_mode"    # 接管模式
    ED = "exit_mode"        # 退出运行模式

#################### 基于风险值判断 ####################
def select_driving_mode(system_risk, driving_risk):
    # 检查输入值是否有效（保持不变）
    if not isinstance(system_risk, (int, float)):
        print("系统风险值无效")
        return DrivingMode.ED
    if not isinstance(driving_risk, (int, float)):
        print("行车风险值无效")
        return DrivingMode.ED

    # 定义隶属度函数
    def triangular(x, a, b, c):
        return max(min((x-a)/(b-a), (c-x)/(c-b)), 0)

    # 模糊化输入变量
    sys_low = triangular(system_risk, 0, 0.3, 0.6)        # 系统风险
    sys_med = triangular(system_risk, 0.3, 0.6, 0.8)
    sys_high = triangular(system_risk, 0.6, 0.8, 1.0)

    drive_low = triangular(driving_risk, 0, 0.3, 0.6)     # 行车风险
    drive_med = triangular(driving_risk, 0.3, 0.6, 0.8)
    drive_high = triangular(driving_risk, 0.6, 0.8, 1.0)

    # 模糊规则库
    rules = [
        # 自动驾驶模式规则
        (min(sys_low, drive_low), DrivingMode.AD),
        (min(sys_low, drive_med), DrivingMode.AD),
        # 降级模式规则
        (min(sys_med, drive_med), DrivingMode.DG),
        (min(sys_low, drive_high), DrivingMode.DG),
        # 接管模式规则 
        (min(sys_high, drive_med), DrivingMode.TD),
        (min(sys_med, drive_high), DrivingMode.TD),
        # 退出模式规则
        (min(sys_high, drive_high), DrivingMode.ED),
        (min(sys_high, drive_low), DrivingMode.ED)
    ]

    # 去模糊化（最大隶属度法）
    max_strength = -1
    driving_mode = DrivingMode.ED
    for strength, mode in rules:
        if strength > max_strength:
            max_strength = strength
            driving_mode = mode

    # 当所有规则强度为0时保持安全模式
    if max_strength <= 0:
        return DrivingMode.ED
        
    return driving_mode


#################### 获取驾驶模式 #################### 
@app.route('/get_driving_mode')
def get_driving_mode():
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            system_risk = data.get('system_risk', '未获取到风险值')
            driving_risk = data.get('driving_risk', '未获取到行车风险')
            driving_mode =  select_driving_mode(system_risk, driving_risk)
        else:
            print(f"[Error] Failed to retrieve data:", response.status_code)
    except Exception as e:
        print(f"[Error] Exception while calling API: {e}")
    
    try:
        response1 = requests.get(url1)
        response2 = requests.get(url2)
        response3 = requests.get(url3)
        response4 = requests.get(url4)
        response5 = requests.get(url5)
        response6 = requests.get(url6)
        response7 = requests.get(url7)
        response8 = requests.get(url8)
        response9 = requests.get(url9)
        response10 = requests.get(url10)

        responses = [response1, response2, response3, response4, response5,
             response6, response7, response8, response9, response10]
        
        if all(r.status_code == 200 for r in responses):
            # ODD元素
            object_data               = response1.json()
            road_information_data     = response2.json()
            weather_data              = response3.json()
            road_infrucstrcution_data = response4.json()
            digtal_data               = response5.json()
            tran_condi_data           = response6.json()
            communica_condi_data      = response7.json()
            driver_data               = response8.json()
            vehicle_data              = response9.json()
            map_local_data            = response10.json()

            # object_flag = object_data[1]
            # road_information_flag = road_information_data[1]
            # weather_flag = weather_data[1]
            # road_infrucstrcution_flag = road_infrucstrcution_data[1]
            # digtal_flag = digtal_data[1]
            # tran_condi_flag = tran_condi_data[1]
            # communica_condi = communica_condi_data[1]
            # map_local_flag = map_local_data[1]
            
        else:
            for r in responses:
                if r.status_code != 200:
                    print(f"[Error] Failed to retrieve data:", response.status_code)
            
    except Exception as e:
        print(f"[Error] Exception while calling API: {e}")

if __name__ == '__main__':
    # 调整端口避免冲突
    app.run(host='127.0.0.1', port=5017, debug=True)