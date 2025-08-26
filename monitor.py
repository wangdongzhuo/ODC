import re
import requests
from flask import Flask,jsonify
import json
import pandas as pd
import time
from collections import defaultdict
import math
from datetime import datetime,timezone
from astral import LocationInfo
from ODC_data.main.call_api_cloud import get_event_info
from ODC_data.main.call_channel import get_channel_state
from astral.sun import sun
from ODCruledata.ODCboundary import ODC
from ODCruledata import vehicle_precondition,ODCrule
from ODC_data.main.call_api_HDmap import query_road_info

app = Flask(__name__)


#UI输出的信息可以如下考虑：
#返回数值的结构为：key;value;red/green;过大/正常范围内/过小(对于数值类型)，异常/正常(对于bool类型)
#对于list类型：
#red/green对应相应的字体颜色

def check_vehicle_runcondition(vehicle):
    yukong_state=True
    yingjian_state=True
    if (vehicle_precondition.validate_yukong(vehicle["域控制器基础信息1"]["data"])==False or vehicle_precondition.validate_yukong2(vehicle["域控制器基础信息2"]["data"])==False):
        yukong_state=False
    elif(vehicle_precondition.validate_taiya(vehicle["胎压监控系统状态"]["data"])== False):
        yingjian_state=False

    #L2状态判断
    LKA_status=False
    ACC_status=False
    AEB_status=True
    xietong_status=False

    LKA_state={'待机','激活'}
    ACC_state={"开启","待机", "激活", "超速控制","初始化"}
    AEB_state={'开启','激活'}
 
    if vehicle["L2功能状态反馈"]["data"]["LKA工作状态"] in LKA_state:
        LKA_status=True
    if vehicle["L2功能状态反馈"]["data"]["ACC工作状态"] in ACC_state:
        ACC_status=True
    if vehicle["L2功能状态反馈"]["data"]["CMS&AEB系统工作状态"] in AEB_state:
        AEB_status=True

    # if vehicle["控制驱动和制动系统报文"]["data"]["协同驾驶启动请求"] == "启动":
        xietong_status=True

    collision_alarm=False
    if vehicle["L2功能状态反馈"]["data"]["CMS&AEB系统工作状态"] == "激活":
        collision_alarm=True    

    door_state=False
    if  vehicle["智能车辆状态反馈"]["data"]["车门状态"]["前门"] == "门已经关" and vehicle["智能车辆状态反馈"]["data"]["车门状态"]["中门"] == "门已经关":
        door_state=True
    vehicle_mode=None
    if  vehicle["L2功能状态反馈"]["data"]["L2功能激活模式"]=="LKA同向协助功能激活":
        vehicle_mode='LKA'
    elif vehicle["L2功能状态反馈"]["data"]["L2功能激活模式"]=="ACC同向协助功能激活":
        vehicle_mode='ACC'
    elif vehicle["L2功能状态反馈"]["data"]["L2功能激活模式"]== "CMS&AEB功能激活":
        vehicle_mode='CMS'
    elif vehicle["L2功能状态反馈"]["data"]["L2功能激活模式"]== "L2功能激活":
        vehicle_mode={'ACC','LKA'}


    turn_light=False
    if  vehicle["智能车辆状态反馈"]["data"]["灯光状态"]["右转向灯"] == "关闭" and vehicle["智能车辆状态反馈"]["data"]["灯光状态"]["左转向灯"] == "关闭":
        turn_light=True
    vehicle_ODD_attribute=True
    result_status = []
    vehicle_state = {
    # '前向防撞功能':vehicle["车辆车速报文"]["data"],
    '协同驾驶状态':('车辆状态','系统功能状态',xietong_status),
    'LKA功能':('车辆状态','系统功能状态',LKA_status),
    'ACC功能':('车辆状态','系统功能状态',ACC_status),
    'AEB功能':('车辆状态','系统功能状态',AEB_status),
    '车速':('车辆状态','车辆运动状态',vehicle["车辆车速报文"]["data"]["车速值"]),
    # '前向距离':math.hypot(vehicle["主目标信息"]["data"]["主目标相对位置X"],vehicle["主目标信息"]["data"]["主目标相对位置Y"]),
    # '纵向加速度':vehicle["车辆加速度信息"]["data"]["加速度数据"]["纵向加速度"]["数值"],
    # '横向加速度':vehicle["车辆加速度信息"]["data"]["加速度数据"]["横向加速度"]["数值"],
    # # '垂向加速度':vehicle["车辆加速度信息"]["data"],
    # '横摆角速度':vehicle["车辆加速度信息"]["data"]["加速度数据"]["横摆角速度"]["数值"],
    # '方向盘转角':vehicle["控制转向系统报文"]["data"]["方向盘角度指令"]["数值"],
    # '前向碰撞预警':collision_alarm,


    '前向距离':('车辆状态','车辆运动状态',70),
    '纵向加速度':('车辆状态','车辆运动状态',10),
    '横向加速度':('车辆状态','车辆运动状态',2),
    # '垂向加速度':vehicle["车辆加速度信息"]["data"],
    '横摆角速度':('车辆状态','车辆运动状态',0),
    '方向盘转角':('车辆状态','车辆运动状态',0),
    '前向碰撞预警':('车辆状态','系统功能预警',collision_alarm),


    # '异常车辆预警':vehicle["车辆车速报文"]["data"],
    # '紧急车辆预警':vehicle["车辆车速报文"]["data"],
    # 'GNSS状态':vehicle["车辆车速报文"]["data"],
    # '域控状态':yukong_state,
    # '总线状态':vehicle["车辆车速报文"]["data"],
    # '以太网状态':vehicle["车辆车速报文"]["data"],
    # '传感器状态':vehicle["主目标信息"]["data"]["感知融合故障"]=="无故障",
    # '计算平台状态':vehicle["车辆车速报文"]["data"], 
    # '硬件状态':yingjian_state, 
    # '系统状态':vehicle["车辆车速报文"]["data"], 
    '异常车辆预警':('车辆状态','系统功能预警',True),
    '紧急车辆预警':('车辆状态','系统功能预警',True),
    'GNSS状态':('车辆状态','系统故障状态',True),
    '域控状态':('车辆状态','系统故障状态',yukong_state),
    '总线状态':('车辆状态','系统故障状态',True),
    '以太网状态':('车辆状态','系统故障状态',True),
    # '传感器状态':vehicle["主目标信息"]["data"]["感知融合故障"]=="无故障",
    '传感器状态':('车辆状态','系统故障状态',True),
    '计算平台状态':('车辆状态','系统故障状态',True), 
    '硬件状态':('车辆状态','系统故障状态',yingjian_state), 
    '系统状态':('车辆状态','系统故障状态',True), 

    '档位':('车辆状态','系统控制状态',vehicle["域控制器基础信息1"]["data"]["当前档位"] == "前进档D"), 
    # '刹车':vehicle["车辆车速报文"]["data"], 
    '刹车':('车辆状态','系统控制状态',True), 
    '电子手刹':('车辆状态','系统控制状态',vehicle["域控制器基础信息1"]["data"]["当前P档位状态"]=="释放"), 



    # '油门开度':vehicle["车辆车速报文"]["data"], 
    '油门开度':('车辆状态','系统控制状态',20), 
    '转向灯关闭':('车辆状态','系统控制状态',turn_light),
    '车辆模式':('车辆状态','系统控制状态',vehicle_mode), 
    # '前雨刮器':[True if vehicle["智能车辆状态反馈"]["data"]["雨刮状态"] in {"off","间歇","低速"} else False], 
    '前雨刮器':('车辆状态','系统控制状态',True), 
    '车门状态':('车辆状态','系统控制状态',door_state), 
    }
    for var_name, (first_cacategory,second_category, var_value) in vehicle_state.items():
        if var_name not in ODCrule.pre_vehicle_rules:
            vehicle_ODD_attribute = False  # 变量未定义规则，直接判定为False
            continue  # 跳过后续规则检查

        rule_func = ODCrule.pre_vehicle_rules[var_name]  # 获取规则函数
        is_valid = rule_func(var_value) 

        if type(var_value) in (int, float):
            try:
                min_val, max_val = ODC[first_cacategory][second_category][var_name]["value"]
            except KeyError:
                min_val, max_val = ODC[first_cacategory][second_category][""]["value"]
            status = "正常范围内" if is_valid else "过大" if var_value > max_val else "过小"
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red", status])
        elif type(var_value) is bool:
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red", "正常" if is_valid else "异常"])
        elif type(var_value) is str:
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red"])
        vehicle_ODD_attribute &= is_valid

    return result_status, vehicle_ODD_attribute,vehicle_state

def get_weather_data():
    api_url = "http://127.0.0.1:5005/get_data"
    try:
        # 发送 GET 请求
        response = requests.get(api_url)
        
        # 检查响应状态码
        if response.status_code == 200:
            data = response.json()  # 解析 JSON 响应
            return data
        else:
            print(f"请求失败，状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")

def check_weather_condition(weather_data):
    is_day=False
    # 设置地理位置为重庆市西部科学城
    location = LocationInfo("Chongqing", "China", "Asia/Shanghai", 29.52349, 106.51285)#此处的经纬度需要修改
    # UNIX时间戳
    timestamp=weather_data['时间帧']
    local_time = datetime.fromtimestamp(timestamp)

    # 获取日出和日落时间
    s = sun(location.observer, date=local_time.date())
    sunrise = s['sunrise'].replace(tzinfo=None)  # 转换为offset-naive时间
    sunset = s['sunset'].replace(tzinfo=None)    # 转换为offset-naive时间
    # 判断是否为白天或晚上
    if sunrise <= local_time <= sunset:
        is_day=True
    is_snow=False
    if weather_data['天气'] in ('LIGHT_SNOW','MODERATE_SNOW','HEAVY_SNOW','STORM_SNOW'):
        is_snow=True
    weather_ODD_attribute=True
    result_status = []
    weather_information = {
        '风': ('环境条件','天气条件', weather_data['风速']),
        '雪': ('环境条件','天气条件', is_snow),
        '雨': ('环境条件','天气条件', weather_data['本地降水量']),
        '气温': ('环境条件','气温', weather_data['气温']),
        '雾霾': ('环境条件','颗粒物', weather_data['AQI值']),
        '光照条件': ('环境条件','光照条件', is_day),
    }

    for var_name, (first_cacategory,second_category, var_value) in weather_information.items():
        if var_name not in ODCrule.pre_weather_rules:
            weather_ODD_attribute = False  # 变量未定义规则，直接判定为False
            continue  # 跳过后续规则检查

        is_valid = all(rule(var_value) for rule in ODCrule.pre_weather_rules[var_name])

            # # 获取 ODC 数据
            # try:
            #     min_val, max_val = ODC["环境条件"][category][var_name]["value"]
            # except KeyError:
            #     print(f"ODC 配置缺失: {category} -> {var_name}")
            #     continue

        if type(var_value) in (int, float):
            try:
                min_val, max_val = ODC[first_cacategory][second_category][var_name]["value"]
            except KeyError:
                min_val, max_val = ODC[first_cacategory][second_category][""]["value"]
            status = "正常范围内" if is_valid else "过大" if var_value > max_val else "过小"
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red", status])
        elif type(var_value) is bool:
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red", "正常" if is_valid else "异常"])
        elif type(var_value) is str:
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red"])
        weather_ODD_attribute &= is_valid

    return result_status, weather_ODD_attribute, weather_information

def check_driver_condition(driver_data):
    result_status = []
    driver_ODD_attribute=True
    attention_states = {'打盹', '打哈欠', '闭眼', '低头', '转头', '打电话', '抽烟', '喝水'}
    seatbelt_states = {'未系安全带'}
    posture_states = {'检测不到人脸', '遮挡摄像头', '佩戴遮阳镜'}

    attention_status = True
    seatbelt_status = True
    posture_status = True

    if driver_data['state_description']  in attention_states:
        attention_status = False
    elif driver_data['state_description']  in seatbelt_states:
        seatbelt_status = False
    elif driver_data['state_description']  in posture_states:
        posture_status = False
    
    driver_state = {
    '注意力状态':('驾乘人员状态','驾驶员状态',attention_status),
    '安全带状态':('驾乘人员状态','驾驶员状态',seatbelt_status),
    '位姿状态':('驾乘人员状态','驾驶员状态',posture_status),
    }
    for var_name, (first_cacategory,second_category, var_value) in driver_state.items():
        if var_name not in ODCrule.pre_driver_rules:
            driver_ODD_attribute = False  # 变量未定义规则，直接判定为False
            continue  # 跳过后续规则检查

        is_valid = all(rule(var_value) for rule in ODCrule.pre_driver_rules[var_name])

        if type(var_value) in (int, float):
            try:
                min_val, max_val = ODC[first_cacategory][second_category][var_name]["value"]
            except KeyError:
                min_val, max_val = ODC[first_cacategory][second_category][""]["value"]
            status = "正常范围内" if is_valid else "过大" if var_value > max_val else "过小"
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red", status])
        elif type(var_value) is bool:
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red", "正常" if is_valid else "异常"])
        elif type(var_value) is str:
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red"])
        driver_ODD_attribute &= is_valid

    return result_status, driver_ODD_attribute, driver_state

def get_vehicle_data():
    url = "http://127.0.0.1:5001/get_can_data"
    last_data = None  # 用于记录上一次的返回数据

    while True:  # 持续循环调用 API
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                # 如果数据和上次相同，则跳过输出
                if data != last_data:
                    last_data = data  # 更新记录的上一次数据
            elif response.status_code == 204:
                # 无新数据时，不输出任何内容
                pass
            else:
                print(f"Error: Received unexpected status code {response.status_code}")
        except Exception as e:
            print(f"[Error] Exception while calling API: {e}")

        # 每隔 1 秒请求一次 API
        time.sleep(1)
        
        # 返回最新的车辆数据
        return last_data

def get_driver_data():
    """调用驾驶员状态监测 API 并格式化输出结果"""
    url = "http://127.0.0.1:5003/get_driver_state"
    last_state = None

    while True:
        try:
            print("\n[信息] 正在获取驾驶员状态...")
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # 如果状态发生变化，则输出详细信息
                if data != last_state:
                    last_state = data
                    return last_state
            elif response.status_code == 404:
                print("[警告] 暂无状态数据")
            else:
                print(f"[错误] 收到意外的状态码 {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("[错误] 无法连接到服务器，请确保服务器已启动")
        except Exception as e:
            print(f"[错误] 调用 API 时发生异常: {str(e)}")
        time.sleep(2)  # 每2秒检测一次

def check_road_attribution(road_data):
    road_ODD_attribute=True
    result_status = []
    is_type_valid=False


# {'道路属性': {'道路类型': {'category': None, 'is_valid': False, 'road_type': None}, 
# '纵断面坡度': 0.0, '道路曲率': 0, '道路曲率半径': inf}, '车道特征': {'是否存在车道': False, '车道数量': 0, '车道宽度': [], '车道标线颜色': []}, 
# '道路设施': {'交通标志': False, '交通信号灯': False}}

    road_information = {
    '区域':('道路属性','道路类型',"地理围栏"),#测试区范围，车辆在不在测试区的多边形中
    '城市道路':('道路属性','道路类型',"主干路"),#有，要补充
    '高速公路':('道路属性','道路类型',"高速公路"),#有，要补充
    '乡村道路':('道路属性','道路类型',False if road_data["道路属性"]["道路类型"]['type'] != "乡村道路" else True),#有，要补充
    '道路表面状况':('道路属性','道路表面',"正常"),#
    '纵断面坡度':('道路属性','道路几何',float(road_data["道路属性"]['道路几何']["纵断面坡度"])),
    '道路曲率半径':('道路属性','道路几何',float(road_data["道路属性"]['道路几何']["道路曲率半径"])),
    '道路交叉':('道路属性','道路几何',"匝道"),
    '标线质量':('道路属性','车道特征',7),#多个标线用哪个
    '车道状态':('道路属性','车道特征',road_data['车道特征']['是否存在车道']),
    '车道宽度':('道路属性','车道特征',3.5),#多个车道用哪个
    '车道标线颜色':('道路属性','车道特征','None' if not road_data['车道特征']['车道标线颜色'][0] else road_data['车道特征']['车道标线颜色'][0]),
    '车道类型':('道路属性','车道特征',road_data['车道特征']['车道类型'][0]),#有，要补充
    '车道数量':('道路属性','车道特征',len(road_data['车道特征']['车道数量']))
    }
    for var_name, (first_cacategory,second_category, var_value) in road_information.items():
        if var_name not in ODCrule.pre_road_rules:
            road_ODD_attribute = False  # 变量未定义规则，直接判定为False
            continue  # 跳过后续规则检查

        is_valid = all(rule(var_value) for rule in ODCrule.pre_road_rules[var_name])
        if type(var_value) in (int, float):
            try:
                min_val, max_val = ODC[first_cacategory][second_category][var_name]["value"]
            except KeyError:
                min_val, max_val = ODC[first_cacategory][second_category][""]["value"]
            status = "正常范围内" if is_valid else "过大" if var_value > max_val else "过小"
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red", status])
        elif type(var_value) is bool:
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red", "正常" if is_valid else "异常"])
        elif type(var_value) is str:
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red"])
        road_ODD_attribute &= is_valid

    return result_status, road_ODD_attribute, road_information

#地图ODD标颜色：整条路经标颜色，车局部标颜色
# def RoutineOdd(routine):
#     #整条路上的ODD颜色就根据路点的信息去检查是不是在ODD边界内，然后局部的话就调用接口，未来一段路上的比较，以最终的结果作为标色的依据，
#     #road_data假定是以列表的形式给出{[x1,y1],[x2,y2],...}
#     whole_ODD=[]
#     for i in range(len(routine)):
#         road_information=query_road_info(routine[0][0],routine[0][1])
#         road_str,road_ODD_attribute=check_road_attribution(road_information)
#         whole_ODD.append({routine[0][0],routine[0][1],road_ODD_attribute})
#     return whole_ODD

def check_road_infrustruction(road_data):

    #缺智能路侧设施、特殊设施，后面补上
    road_infrustruction_ODD_attribute=True
    result_status = []

# {'道路属性': {'道路类型': {'category': None, 'is_valid': False, 'road_type': None}, 
# '纵断面坡度': 0.0, '道路曲率': 0, '道路曲率半径': inf}, '车道特征': {'是否存在车道': False, '车道数量': 0, '车道宽度': [], '车道标线颜色': []}, 
# '道路设施': {'交通标志': False, '交通信号灯': False}}

    road_infrustruction_info = {
    '交通标志':('道路设施','道路交通设施',road_data['道路设施']['交通信号灯']),
    '交通信号灯':('道路设施','道路交通设施',road_data['道路设施']['交通信号灯']),
    '智能路侧设施':('道路设施','智能路侧设施',100),#缺
    '特殊设施':('道路设施','特殊设施','减速带'),#缺
    }
    for var_name, (first_cacategory,second_category, var_value) in road_infrustruction_info.items():
        if var_name not in ODCrule.pre_road_infrustrction_rules:
            road_infrustruction_ODD_attribute = False  # 变量未定义规则，直接判定为False
            continue  # 跳过后续规则检查

        is_valid = all(rule(var_value) for rule in ODCrule.pre_road_infrustrction_rules[var_name])
        if type(var_value) in (int, float):
            try:
                min_val, max_val = ODC[first_cacategory][second_category][var_name]["value"]
            except KeyError:
                min_val, max_val = ODC[first_cacategory][second_category][""]["value"]
            status = "正常范围内" if is_valid else "过大" if var_value > max_val else "过小"
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red", status])
        elif type(var_value) is bool:
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red", "正常" if is_valid else "异常"])
        elif type(var_value) is str:
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red"])
        road_infrustruction_ODD_attribute &= is_valid

    return result_status, road_infrustruction_ODD_attribute,road_infrustruction_info

def check_digtal_info_rule(digtal_info):
    digtal_info_ODD_attribute=True
    result_status = []

    digtal_info = {
    '消息体':("数字信息","消息体",digtal_info['数字信息']['消息体']),#缺
    }

    for var_name, (first_cacategory,second_category, var_value) in digtal_info.items():
        if var_name not in ODCrule.pre_digtal_info_rule_rules:
            digtal_info_ODD_attribute = False  # 变量未定义规则，直接判定为False
            continue  # 跳过后续规则检查

        is_valid = all(rule(var_value) for rule in ODCrule.pre_digtal_info_rule_rules[var_name])

        if type(var_value) in (int, float):
            try:
                min_val, max_val = ODC[first_cacategory][second_category][var_name]["value"]
            except KeyError:
                min_val, max_val = ODC[first_cacategory][second_category][""]["value"]
            status = "正常范围内" if is_valid else "过大" if var_value > max_val else "过小"
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red", status])
        elif type(var_value) is bool:
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red", "正常" if is_valid else "异常"])
        elif type(var_value) is str:
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red"])
        digtal_info_ODD_attribute &= is_valid

    return result_status, digtal_info_ODD_attribute,digtal_info

def check_object_rule(object_info):
    object_info_ODD_attribute=True
    result_status = []

    object_state = {
    '目标物类型':('目标物','目标物类型',object_info["目标物"]["目标物类型"]),#缺
    }
    for var_name, (first_cacategory,second_category, var_value) in object_state.items():
        if var_name not in ODCrule.pre_object_rules:
            object_info_ODD_attribute = False  # 变量未定义规则，直接判定为False
            continue  # 跳过后续规则检查

        is_valid = all(rule(var_value) for rule in ODCrule.pre_object_rules[var_name])
        if type(var_value) in (int, float):
            try:
                min_val, max_val = ODC[first_cacategory][second_category][var_name]["value"]
            except KeyError:
                min_val, max_val = ODC[first_cacategory][second_category][""]["value"]
            status = "正常范围内" if is_valid else "过大" if var_value > max_val else "过小"
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red", status])
        elif type(var_value) is bool:
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red", "正常" if is_valid else "异常"])
        elif type(var_value) is str:
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red"])
        object_info_ODD_attribute &= is_valid

    return result_status, object_info_ODD_attribute,object_state



def check_tran_condi_rule(tran_condi):
    tran_condi_ODD_attribute=True
    result_status = []

    tran_condi_info = {
    '交通事件':('交通条件','交通事件',tran_condi["交通条件"]["交通事件"]),#有，要补充
    '交通拥堵度':('交通条件','交通拥堵度',tran_condi["交通条件"]["交通拥堵度"]),#有，要补充
    '可协作车辆':('交通条件','可协作车辆',tran_condi["交通条件"]["可协作车辆"]),#
    '交通法规':('交通条件','交通法规',tran_condi["交通条件"]["交通法规"]),#有，要补充
    }
    for var_name, (first_cacategory,second_category, var_value) in tran_condi_info.items():
        if var_name not in ODCrule.pre_tran_condi_rules:
            tran_condi_ODD_attribute = False  # 变量未定义规则，直接判定为False
            continue  # 跳过后续规则检查

        is_valid = all(rule(var_value) for rule in ODCrule.pre_tran_condi_rules[var_name])
        if type(var_value) in (int, float):
            try:
                min_val, max_val = ODC[first_cacategory][second_category][var_name]["value"]
            except KeyError:
                min_val, max_val = ODC[first_cacategory][second_category][""]["value"]
            status = "正常范围内" if is_valid else "过大" if var_value > max_val else "过小"
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red", status])
        elif type(var_value) is bool:
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red", "正常" if is_valid else "异常"])
        elif type(var_value) is str:
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red"])
        tran_condi_ODD_attribute &= is_valid

    return result_status, tran_condi_ODD_attribute,tran_condi_info

def check_communica_rule(communica_data):
    communica_ODD_attribute=True
    result_status = []

    communica_info = {
    '丢包率':('通讯与计算','丢包率',communica_data["通讯与计算"]["丢包率"]),
    '通信模式':('通讯与计算','通信模式',communica_data["通讯与计算"]["通信模式"]),
    '通信时延':('通讯与计算','通信时延',communica_data["通讯与计算"]["通信时延"]),
    # '协同自适应巡航':('通讯与计算','通信时延',communica_info["通讯与计算"]["通信时延"]["协同自适应巡航"]),
    # '无信号匝道的转向或交替通行':('通讯与计算','通信时延',communica_info["通讯与计算"]["通信时延"]["无信号匝道的转向或交替通行"]),
    # '协作式变道':('通讯与计算','通信时延',communica_info["通讯与计算"]["通信时延"]["协作式变道"]),
    # '路口对向行驶车辆的无保护左转':('通讯与计算','通信时延',communica_info["通讯与计算"]["通信时延"]["路口对向行驶车辆的无保护左转"]),
    # '协作式车道汇入':('通讯与计算','通信时延',communica_info["通讯与计算"]["通信时延"]["协作式车道汇入"]),
    # '编队行驶':('通讯与计算','通信时延',communica_info["通讯与计算"]["通信时延"]["编队行驶"]),
    # '动态车速限制':('通讯与计算','通信时延',communica_info["通讯与计算"]["通信时延"]["动态车速限制"]),
    # '远程控制驾驶':('通讯与计算','通信时延',communica_info["通讯与计算"]["通信时延"]["远程控制驾驶"]),
    }
    for var_name, (first_cacategory,second_category, var_value) in communica_info.items():
        if var_name not in ODCrule.pre_communica_rules:
            communica_ODD_attribute = False  # 变量未定义规则，直接判定为False
            continue  # 跳过后续规则检查

        is_valid = all(rule(var_value) for rule in ODCrule.pre_communica_rules[var_name])

            # # 获取 ODC 数据
            # try:
            #     min_val, max_val = ODC["环境条件"][category][var_name]["value"]
            # except KeyError:
            #     print(f"ODC 配置缺失: {category} -> {var_name}")
            #     continue

        if type(var_value) in (int, float):
            try:
                min_val, max_val = ODC[first_cacategory][second_category][var_name]["value"]
            except KeyError:
                min_val, max_val = ODC[first_cacategory][second_category][""]["value"]
            status = "正常范围内" if is_valid else "过大" if var_value > max_val else "过小"
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red", status])
        elif type(var_value) is bool:
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red", "正常" if is_valid else "异常"])
        elif type(var_value) is str:
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red"])
        communica_ODD_attribute &= is_valid

    return result_status, communica_ODD_attribute,communica_info

def check_map_local_rule():
    map_local_ODD_attribute=True
    result_status = []

    map_info = {
    '地图':('地图与定位','地图',True),#缺
    '定位系统':('地图与定位','定位系统','北斗'),#缺
    }
    for var_name, (first_cacategory,second_category, var_value) in map_info.items():
        if var_name not in ODCrule.pre_map_local_rules:
            map_local_ODD_attribute = False  # 变量未定义规则，直接判定为False
            continue  # 跳过后续规则检查

        is_valid = all(rule(var_value) for rule in ODCrule.pre_map_local_rules[var_name])
        if type(var_value) in (int, float):
            try:
                min_val, max_val = ODC[first_cacategory][second_category][var_name]["value"]
            except KeyError:
                min_val, max_val = ODC[first_cacategory][second_category][""]["value"]
            status = "正常范围内" if is_valid else "过大" if var_value > max_val else "过小"
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red", status])
        elif type(var_value) is bool:
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red", "正常" if is_valid else "异常"])
        elif type(var_value) is str:
            result_status.append([first_cacategory,second_category,var_name,var_value, "green" if is_valid else "red"])
        map_local_ODD_attribute &= is_valid
    return result_status, map_local_ODD_attribute,map_info

def get_traffic_status(center_lat, center_lng, radius=100, api_key='c4f1e88fb7df0edf52c0b0fc9a84dec1'):
    """
    查询圆形区域内的交通拥堵信息和交通事件信息
    :param center_lat: 圆心纬度
    :param center_lng: 圆心经度
    :param radius: 圆形区域半径（单位：米）
    :param api_key: 高德API Key
    :return: 查询结果
    """
    url = "https://restapi.amap.com/v3/traffic/status/circle"
    params = {
        "key": api_key,
        "location": f"{center_lng},{center_lat}",  # 经度在前，纬度在后
        "radius": radius,
        "extensions": "base"  # 返回完整信息，包括交通事件
    }

    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "1":
            return data
        else:
            print(f"Error: {data['info']}")
            return None
    else:
        print(f"HTTP Error: {response.status_code}")
        return None


# #车端数据
# # 发送 GET 请求到接口,获得车端的数据

vehicle = get_vehicle_data()
# # print(vehicle["域控制器基础信息1"]['data']["当前档位"])

vehicle_run_str,odd,ele=check_vehicle_runcondition(vehicle)

def get_event_info():
    url = 'http://127.0.0.1:5004/get_event_info'
    try:
        response = requests.get(url)

        if response.status_code == 200:
            # 解析并打印返回的中文解读数据
            data = response.json()
            return data
            # # 输出所有事件数据
            # print("API 返回的事件信息解读：")
            # for event in data:
            #     print(f"\n事件ID: {event['事件ID']}")
            #     print(f"车辆ID: {event['车辆ID']}")
            #     print(f"事件类型: {event['事件类型']}")
            #     print(f"事件优先级: {event['事件优先级']}")
            #     print(f"预计速度: {event['预计速度']}")
            #     print(f"最大速度: {event['最大速度']}")
            #     print(f"最小速度: {event['最小速度']}")
            #     print(f"交叉口数量: {event['交叉口数量']}")
            #     print(f"行为类型: {event['行为类型']}")
            #     print(f"与停止线的距离: {event['与停止线的距离']}")
            #     print(
            #         f"事件位置: 纬度={event['事件位置']['纬度']} 经度={event['事件位置']['经度']} 海拔={event['事件位置']['海拔']}")
            #     print(f"事件发生时间戳: {event['事件发生时间戳']}")
            #     print(f"UUID: {event['UUID']}")
        else:
            print(f"Error: {response.status_code}")
            print("错误详情:", response.text)  # 输出错误详情

    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")


# center_latitude = 28.19063009  # 圆心纬度
# center_longitude =  106.1871641414752596  # 圆心经度
# center_latitude = 29.568271  # 圆心纬度
# center_longitude =  106.363359  # 圆心经度
# result = get_traffic_status(center_latitude, center_longitude)
# print(result)





#目标物
#缺失
object={'目标物':{'目标物类型':'行人'}}
object_info_str=check_object_rule(object)#可检查部分

#道路属性
# longitude=1.1871641414752596,
# latitude=28.190630091477217,
coordinates = [(106.363359, 29.568271)]
road_information=query_road_info(coordinates[0][0],coordinates[0][1])
result_status,road_ODD_attribute,pre_road_rules=check_road_attribution(road_information)

# #环境条件
weather_data=get_weather_data()
weather_str=check_weather_condition(weather_data)

#道路设施
road_infrucstrcution_str=check_road_infrustruction(road_information)#可检查部分

#数字信息
#缺失，先按照有的来写，最后补充完整
digtal={'数字信息':{'消息体':True,'信源发送频率':True}}
digtal_info_str=check_digtal_info_rule(digtal)#可检查部分

#交通条件
#缺失，先按照有的来写，最后补充完整


# center_latitude = 39.98641364  # 圆心纬度
# center_longitude =  116.3057764  # 圆心经度
# result = get_traffic_status(center_latitude, center_longitude)
tran_condi={'交通条件':{'交通事件':False,'交通拥堵度':'缓行','可协作车辆':True,'交通法规':True}}
tran_condi_info_str=check_tran_condi_rule(tran_condi)#可检查部分

#通讯与计算
#缺失，先按照有的来写，最后补充完整
communica_condi={'通讯与计算':{'丢包率':0.01,'通信模式':'V2N','通信时延':15}}
communica_condi_info_str=check_communica_rule(communica_condi)#可检查部分

#地图与定位
#缺失，先按照有的来写，最后补充完整
# map_local={'地图与定位':{'地图':True,'定位系统':'北斗'}}
map_local_info_str=check_map_local_rule()#可检查部分

#驾驶员状态
driver_data=get_driver_data()
# print(driver_data['state_description'])
driver_str=check_driver_condition(driver_data)


#调用接口，将元素保存在本地，注：所有元素的值都需要保存，时间，还有是否在边界内








