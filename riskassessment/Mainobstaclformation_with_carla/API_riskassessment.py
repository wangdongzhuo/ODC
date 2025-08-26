from ODCelementcarla import *
from flask import Flask, jsonify, Response
import numpy as np
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.contour import QuadContourSet
import cv2
from prompt_toolkit.filters import renderer_height_is_known
import math
import base64
from io import BytesIO
import time
import io
from enum import Enum

current_dr_info = []
app = Flask(__name__)  # 使用 Flask 类创建一个应用实例，__name__传递给Flask，帮助它确定应用所在的模块。Flask 类是Flask框架的核心，所有的Web应用配置和路由都基于此实例。

def element_trans():
    url1 = "http://127.0.0.1:5001/get_can_data"
    url2 = "http://127.0.0.1:5003/get_driver_state"
    url3 = "http://127.0.0.1:5012/get_position_data"
    last_data1 = None  # 用于记录上一次的返回数据
    last_data2 = None  # 用于记录上一次的返回数据
    last_data3 = None  # 用于记录上一次的返回数据
    while True:  # 持续循环调用 API 
        try:
            response1 = requests.get(url1)
            response2 = requests.get(url2)
            response3 = requests.get(url3)
            if response1.status_code == 200 and response2.status_code == 200 and response3.status_code == 200:
                data1 = response1.json()
                data2 = response2.json()
                data3 = response3.json()

                # 如果数据和上次相同，则跳过输出
                if data1 != last_data1:
                    data1 = json.dumps(data1, indent=4, ensure_ascii=False)  # 格式化输出 JSON 数据
                    can_data = json_string_to_dict(data1)
                    last_data1 = data1  # 更新记录的上一次数据
                if data2 != last_data2:
                    driver_data = data2
                    last_data2 = data2
                if data3 != last_data3:
                    position_data = data3
                    last_data3 = data3
                dataupdate(can_data, driver_data, position_data)
                return can_data, driver_data, position_data 
            elif response1.status_code == 204:
                # 无新数据时，不输出任何内容
                pass
            else:
                print(f"Error: Received unexpected status code {response1.status_code}")
        except Exception as e:
            print(f"[Error] Exception while calling API: {e}")

        # 每隔 1 秒请求一次 API
        time.sleep(1)


def remove_zeros(input_list):
    return [x for x in input_list if x != 0]


def ZOrisk():
    # 将变量放入列表
    check_list = []
    # if True == CardoorState.launchstate:
    #     check_list.append(CardoorState.state)
    if True == L2FuStfeedback.launchstate:
        check_list.append(L2FuStfeedback.accstate)
        check_list.append(L2FuStfeedback.lkastate)
        check_list.append(L2FuStfeedback.ldwstate)
        check_list.append(L2FuStfeedback.cmsaebstate)
    if True == DDTfeedbackstate.launchstate1:
        check_list.append(DDTfeedbackstate.safetybelt)
        check_list.append(DDTfeedbackstate.driverleft)
    if True == Preceivepartstate.launchstate:
        # check_list.append(Preceivepartstate.camera)
        # check_list.append(Preceivepartstate.radar)
        check_list.append(Preceivepartstate.vehicleconnect)
        check_list.append(Preceivepartstate.fusion)
    print(check_list, 'check_list')
    zo = False in check_list
    if zo == True:
        zorisk = 100
    else:
        zorisk = 0
    print(zorisk, 'zorisk')
    return zorisk


def Levelrisk():
    dataclasses = [SystemFault.lowpressure_tlevel, SystemFault.highpressure_tlevel,
                   SystemFault.breakstate_tlevel, DDTfeedbackstate.tstatelevel]
    # print(DDTfeedbackstate.safetybelt,"DDTfeedbackstate.safetybelt")
    risklevelm = []
    for index in dataclasses:
        risklist = np.linspace(0, 100, index + 1).tolist()
        risklevelm.append(risklist)
    risklevel = [SystemFault.lowpressure, SystemFault.highpressure, SystemFault.breakstate, DDTfeedbackstate.tstate]
    riskvalue = []
    init = 0
    for i in risklevel:
        riskvalue.append(risklevelm[init][i])
        init += 1
    riskvalue = remove_zeros(riskvalue)
    if len(riskvalue) == 0:
        levelrisk = 0
    else:
        try:
            levelrisk = np.prod(riskvalue) / (100 ** (len(riskvalue) - 1))  # 按等级划分风险值为均分
        except:
            levelrisk = 0
    print(levelrisk, 'levelrisk')
    return round(levelrisk, 2)


def Constantrisk(conditions):
    # 贝叶斯概率计算初始矩阵
    Weather = np.array([
        [0.35, 0.7],  # clear
        [0.20, 0.2],  # cloudy
        [0.30, 0.05],  # rain
        [0.15, 0.05]  # fog
    ])
    Lighting = np.array([
        [0.30, 0.7],  # daylight
        [0.10, 0.1],  # dawn/dusk
        [0.25, 0.1],  # dark-lighting
        [0.35, 0.1]  # dark
    ])
    car_lane_status = np.array([
        [0.05, 0.7],  # 清晰可见
        [0.25, 0.2],  # 模糊
        [0.70, 0.1]  # 缺失
    ])
    road_type = np.array([
        [0.20, 0.8],  # 快速路
        [0.80, 0.2]  # 其他类型
    ])
    road_sign_instracture = np.array([
        [0.10, 0.9],  # 有标志
        [0.90, 0.1]  # 无标志
    ])
    traffic_light = np.array([
        [0.10, 0.9],  # 有信号灯
        [0.90, 0.1]  # 无信号灯
    ])
    PH = 0.03  # 先验概率
    # 解析条件参数
    (weather_idx, lighting_idx, lane_idx, road_type_idx, sign_idx, light_idx) = conditions
    # 计算PXH0和PXH1
    PXH0 = (
            Weather[weather_idx, 0] *
            Lighting[lighting_idx, 0] *
            car_lane_status[lane_idx, 0] *
            road_type[road_type_idx, 0] *
            road_sign_instracture[sign_idx, 0] *
            traffic_light[light_idx, 0]
    )

    PXH1 = (
            Weather[weather_idx, 1] *
            Lighting[lighting_idx, 1] *
            car_lane_status[lane_idx, 1] *
            road_type[road_type_idx, 1] *
            road_sign_instracture[sign_idx, 1] *
            traffic_light[light_idx, 1]
    )

    # 计算后验概率
    P = ((PXH0 * PH) / (PXH0 * PH + PXH1 * (1 - PH))) * 100
    return round(P, 2)


def Calculate_TTC():
    relvel = np.sqrt(Mainobstaclformation.relvelx ** 2 + Mainobstaclformation.relvely ** 2)
    distance = np.sqrt(Mainobstaclformation.posx ** 2 + Mainobstaclformation.posy ** 2)
    TTC = distance / relvel
    # TTC_lon = Mainobstaclformation.posx / Mainobstaclformation.relvelx
    # TTC_lat = Mainobstaclformation.posy / Mainobstaclformation.relvely
    # return TTC_lon, TTC_lat
    return TTC


def RiskField():
    A = 5.0
    kv = 0.5  # 调整为更小的值
    alpha = 0.2
    L_obs = 5.0
    if not hasattr(Mainobstaclformation, 'relvelx') or not Mainobstaclformation.launchstate:
        print("Mainobstaclformation 未初始化或无主目标")
        return 0.0
    sigma_v = kv * np.abs(Mainobstaclformation.relvelx)
    sigma_y = 20  # 调整为更小的值
    relv = -1 if Mainobstaclformation.relvelx < 0 else 1
    numerator = A * np.exp(
        -(Mainobstaclformation.posx ** 2 / sigma_v ** 2) - (Mainobstaclformation.posy ** 2 / (sigma_y ** 2)))
    denominator = 1 + np.exp(relv * (Mainobstaclformation.posy - alpha * L_obs * relv))
    vehicle_risk = numerator / denominator
    return vehicle_risk

def RiskField_radio(rel_posx,rel_posy):
    A = 5.0
    kv = 0.5  # 调整为更小的值
    alpha = 0.2
    L_obs = 5.0
    if not hasattr(Mainobstaclformation, 'relvelx') or not Mainobstaclformation.launchstate:
        print("Mainobstaclformation 未初始化或无主目标")
        return 0.0
    sigma_v = kv * np.abs(Mainobstaclformation.relvelx)
    sigma_y = 0.5  # 调整为更小的值
    relv = -1 if Mainobstaclformation.relvelx < 0 else 1
    numerator = A * np.exp(
        -(rel_posx ** 2 / sigma_v ** 2) - (rel_posy ** 2 / (sigma_y ** 2)))
    denominator = 1 + np.exp(relv * (rel_posy - alpha * L_obs * relv))
    vehicle_risk = numerator / denominator
    return vehicle_risk

def Update_Risk_Field(frame, ax, theta, r, posx_grid, posy_grid):
    risk_fields = []
    risk_field_max = 5.0

    # 检查 Mainobstaclformation 是否有效
    if not hasattr(Mainobstaclformation, 'launchstate') or not Mainobstaclformation.launchstate:
        combined_risk_field = np.zeros_like(posx_grid)
        # print("No valid Mainobstaclformation data")
    else:
        # print("Mainobstaclformation.posx:", Mainobstaclformation.posx)
        # print("Mainobstaclformation.relvelx:", Mainobstaclformation.relvelx)
        risk_field = np.zeros_like(posx_grid)
        # print("Calculating risk field...")
        for i in range(posx_grid.shape[0]):
            for j in range(posx_grid.shape[1]):
                rel_posx = posx_grid[i, j] - Mainobstaclformation.posx
                rel_posy = posy_grid[i, j] - Mainobstaclformation.posy
                risk_field[i, j] = RiskField_radio(rel_posx, rel_posy)
        risk_fields.append(risk_field)
        combined_risk_field = np.max(risk_fields, axis=0)
        # print("Max risk field value:", np.max(combined_risk_field))

    # 限制风险值范围
    combined_risk_field = np.clip(combined_risk_field, 0, risk_field_max)
    combined_risk_field = np.round(combined_risk_field, decimals=6)

    # 清除旧的轮廓图
    for c in ax.collections:
        if isinstance(c, QuadContourSet):
            c.remove()

    # 绘制新轮廓图
    contour = ax.contourf(theta, r, combined_risk_field, cmap='Reds', levels=np.linspace(0, risk_field_max, 256))
    contour.set_clim(0, risk_field_max)
    return (contour,)

def Generate_Radio_Frame(detection_range):
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
    try:
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        theta = np.linspace(0, 2 * np.pi, 100)
        r = np.linspace(0, detection_range, 100)
        theta, r = np.meshgrid(theta, r)
        posx_grid = r * np.cos(theta)
        posy_grid = r * np.sin(theta)

        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        ax.set_rlabel_position(0)

        # 初始化空的轮廓图
        risk_field_max = 5
        contour = ax.contourf(theta, r, np.zeros_like(posx_grid), cmap='Reds',
                              levels=np.linspace(0, risk_field_max, 256))
        contour.set_clim(0, risk_field_max)

        # 更新风险场
        Update_Risk_Field(0, ax, theta, r, posx_grid, posy_grid)

        cbar = plt.colorbar(contour, ax=ax, label='风险值')
        cbar.set_ticks(np.linspace(0, risk_field_max, 6))
        plt.title('风险场雷达图')

        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img = cv2.imdecode(np.frombuffer(buf.getvalue(), np.uint8), cv2.IMREAD_COLOR)
        return img
    finally:
        plt.close(fig)
        plt.close("all")

def generate_video_stream(detection_range=30):
    while True:
        try:
            can_data, driver_data,position_data = element_trans()
            dataupdate(can_data, driver_data,position_data)
            frame = Generate_Radio_Frame(detection_range)
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                print("帧编码失败")
                continue
            frame_data = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
            time.sleep(0.1)
        except Exception as e:
            print(f"生成视频流时出错: {e}")
            break


@app.route('/video_feed')
def video_feed():
    print("Received /video_feed request")
    print("正在启动视频流服务...")
    print("视频流地址: http://127.0.0.1:5010/video_feed")
    print("视频流服务已成功启动")
    return Response(generate_video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


def evaluate_risk(value):
    if value < 10:
        level = 0
    elif 10 <= value < 30:
        level = 1
    elif 30 <= value < 50:
        level = 2
    elif 50 <= value < 70:
        level = 3
    else:  # 70 <= value <= 100
        level = 4
    if level == 0 or level == 1:
        risklevel = '低'
    elif level == 2:
        risklevel = '中'
    elif level == 3 or level == 4:
        risklevel = '高'
    return level, risklevel


def classify_weather(input_dict):
    weather_mapping = {
        # 晴朗类（包含所有晴天的变体）
        '晴': '晴朗', '晴（白天）': '晴朗', '晴（夜间）': '晴朗',
        # 多云类（包含阴天）
        '多云': '多云', '多云（白天）': '多云', '多云（夜间）': '多云', '阴': '多云',
        # 雨类（包含所有降水强度）
        '雨': '雨', '小雨': '雨', '中雨': '雨', '大雨': '雨', '暴雨': '雨',
        # 雾类
        '雾': '雾',
        # 特殊天气归为其他
        '浮尘': '其他', '沙尘': '其他', '大风': '其他',
        '小雪': '其他', '中雪': '其他', '大雪': '其他', '暴雪': '其他'
    }
    return {
        '天气': weather_mapping.get(input_dict['天气'], '其他'),
        '原始数据': input_dict['天气']
    }


def Conditions_decide(weather_data):
    # 输入conditions(weather[0clear,1cloudy,2rain,3fog], lighting[0daylight,1dawn/dusk,2dark-lighting,3dark],
    # lane[0clear,1blur,2missing], road_type[0highway,1other], sign[0yes,1no], light[0yes,1no])
    # 输入字典示例（包含所有可能的天气类型）
    try:
        weather_data = classify_weather(weather_data)
        weather_data = weather_data['天气']
        if weather_data == '晴朗':
            conditionsweather = 0
        elif weather_data == '多云':
            conditionsweather = 1
        elif weather_data == '雨':
            conditionsweather = 2
        elif weather_data == '雾':
            conditionsweather = 3
        elif weather_data == '其他':
            conditionsweather = 1
    except:
        weather_data = False
        conditionsweather = 1
    conditionslighting = 0
    if Roadlinestate1.confidence > 0.8:
        conditionslane = 0
    elif Roadlinestate1.confidence > 0.5:  # 标线2未加
        conditionslane = 1
    else:
        conditionslane = 2
    conditionsroadtype = 1
    conditionssign = 0
    conditionslight = 1
    conditions = (
    conditionsweather, conditionslighting, conditionslane, conditionsroadtype, conditionssign, conditionslight)
    return conditions

class DrivingMode(Enum):
    AD = "autonomous_mode"  # 自动驾驶模式
    DG = "degraded_mode"    # 降级模式
    TD = "takeover_mode"    # 接管模式
    ED = "exit_mode"        # 退出运行模式

#################### 基于风险值的驾驶模式选择 ####################
def select_driving_mode(system_risk, driving_risk, TTC):
    # 检查输入值是否有效
    if not isinstance(system_risk, (int, float)):
        print("系统风险值无效")
        return DrivingMode.ED
    if not isinstance(driving_risk, (int, float)):
        print("行车风险值无效")
        return DrivingMode.ED
    if not isinstance(TTC, (int, float)):
        print("TTC值无效")
        return DrivingMode.ED

    # 自动驾驶模式条件
    if system_risk < 0.3 and driving_risk < 0.3 and TTC > 3.0:
        driving_mode = DrivingMode.AD
    # 降级模式条件
    elif 0.3 <= system_risk < 0.6 and 0.3 <= driving_risk < 0.6 and TTC > 2.0:
        driving_mode = DrivingMode.DG
    # 接管模式条件
    elif 0.6 <= system_risk < 0.8 and 0.6 <= driving_risk < 0.8 and TTC > 1.5:
        driving_mode = DrivingMode.TD
    # 退出模式条件
    else:
        driving_mode = DrivingMode.ED

    return driving_mode

@app.route('/risk_value')
def risk_mix():
    if True:
        interval = 1  # 调用数据频率（单位:s/次
        can_data, driver_data,position_data = element_trans()
        Power_trigger = True  # 点火开关置为启动
        Auto_trigger = True  # 自动驾驶开关置为启动
        while (Power_trigger == True):
            while Auto_trigger:
                weather_data = {'天气': ['晴（白天）', '晴（夜间）', '多云（白天）', '多云（夜间）', '大雨', '中雨',
                                       '小雨', '雾', '浮尘', '沙尘', '大风', '小雪', '中雪', '大雪', '暴雪']}
                zorisk = ZOrisk()
                levelrisk = Levelrisk()
                # 连续型风险类
                conditions = Conditions_decide(weather_data)
                # print(conditions,'conditions')
                constantrisk = Constantrisk(conditions)
                print(can_data["驱动状态报文"]["timestamp"])
                print(constantrisk, 'constantrisk')
                system_risk = max(zorisk, levelrisk, constantrisk)
                [num_level, str_level] = evaluate_risk(system_risk)
                response = {}
                response['system_risk'] = system_risk
                response['num_level'] = num_level
                response['str_level'] = str_level
                try:
                    driving_risk = RiskField()  # 行车风险
                    response['driving_risk'] = driving_risk
                except:
                    response['driving_risk'] = "无主目标，无需计算行车风险"
                try:
                    TTC = Calculate_TTC()  # 行车风险
                    response['TTC'] = TTC
                except:
                    response['TTC'] = "无主目标， TTC为安全值"
                driving_mode_o = select_driving_mode(system_risk / 100, driving_risk, TTC)
                driving_mode = driving_mode_o.value
                response['driving_mode'] = driving_mode
                return jsonify(response)
        else:
            print('点火开关未启动')
    # 返回JSON响应


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5010,
            debug=True)
    # app.run(host='0.0.0.0', port=5010,
    #         debug=True)  # 启动Flask开发服务器，使应用在 127.0.0.1:5001 地址上运行。debug=True 启用调试模式，这样你可以在开发过程中看到错误信息，并且服务器在代码修改时会自动重新加载。
