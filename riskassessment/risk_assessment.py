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
posx = 30 
posy = 5 
relvelx = 6 
relvely = 2
# mian_ob_information = {
#     "posx": 30,
#     "posy": 5,
#     "relvelx": 6,
#     "relvely": 2
# }

def add_function(v, limit):# 定义上升曲线
    v0 = limit
    n = 1.5  # 调整函数陡峭度
    k = np.log(20) / (n * limit-1.05*v0)  # 调整函数陡峭度，可通过调节n来改变陡峭度
    if float(200 / (1 + np.exp(-k * (v - v0))) <= 100):
        return round(float(200 / (1 + np.exp(-k * (v - v0)))), 3)
    else:
        return 100

def normalize(odc_dict, odc_value_dict):# 归一化处理
    if odc_dict['type'] == 1: # 1表示只有0，1两个值的ODC元素
        if odc_value_dict['ODC元素值'] == True:
            return add_function(0, 1)
        else:
            return add_function(1, 1)
    elif odc_dict['type'] == 2.1: # 2.1表示对称元素
        max_val = odc_dict['ODC边界'][-1]
        value = odc_value_dict['ODC元素值']
        if value >= max_val:
            return add_function(1, 1)
        else:
            return add_function(abs(value) / (max_val), 1)
    elif odc_dict['type'] == 2.2: # 2.2表示非对称元素
        min_val = odc_dict['ODC边界'][0]
        max_val = odc_dict['ODC边界'][-1]
        value = odc_value_dict['ODC元素值']
        if min_val <= value <= max_val:
            mid_val = (abs(min_val) + abs(max_val)) / 2
            nom_value = abs(value - mid_val) / (mid_val)
            return add_function(nom_value, 1) 
        else:
            return add_function(1, 1)
    elif odc_dict['type'] == 3.1:
        min_val = odc_dict['ODC边界'][0]
        max_val = odc_dict['ODC边界'][-1]
        value = odc_value_dict['ODC元素值']
        if value <= min_val and min_val != 0:
            return add_function(1, 1)
        else:
            if value >= max_val:
                return add_function(0, 1)
            else:
                nor_value = abs(value - max_val) / (max_val - min_val)
                return nor_value 
    elif odc_dict['type'] == 3.2:
        min_val = odc_dict['ODC边界'][0]
        max_val = odc_dict['ODC边界'][-1]
        value = odc_value_dict['ODC元素值']
        if value >= max_val:
            return add_function(1, 1)
        else:
            if value <= min_val:
                return add_function(0, 1)
            else:
                nor_value = abs(value - min_val) / (max_val - min_val)
                return add_function(nor_value, 1) 
    elif odc_dict['type'] == 4:
        value = odc_value_dict['ODC元素值']
        if value in odc_dict['ODC边界']:
            return add_function(0, 1)
        else:
            return add_function(1, 1)
    elif odc_dict['type'] == 5:
        value = odc_value_dict['ODC元素值']
        min_val = odc_dict['ODC边界'][0]
        max_val = odc_dict['ODC边界'][-1]
        if min_val<=value<=max_val:
            return add_function(0, 1)
        else:
            return add_function(1, 1)            
        
def calculate_risk_value(norvalue):# 计算单个ODC元素风险值
    risk_value = []
    for i in norvalue:
        risk_value.append({'ODC元素': i['ODC元素'], '风险值': add_function(i['归一化数值'], 1)})
    return risk_value

def leadto(KEY_INDEX_MAP, keyname):
    index = KEY_INDEX_MAP.get(keyname)
    if index is None:
        print(f'未识别的键值{keyname}')
        return -1  # 返回-1表示无效键，可根据需求调整
    return index

def build_nested_dict(data_list):
    result = {}
    for item in data_list:
      # 提取关键字段
      main_key = item[0]
      second_key = item[1]
      third_key = item[2]
      value = item[3]  # 第四列为值
      
      # 创建主分类
      if main_key not in result:
          result[main_key] = {}
      
      # 处理2层结构
      if second_key == third_key:  # 2层结构
          result[main_key].setdefault(second_key, {'ODC元素值':value})
      else:  # 3层结构
          if second_key not in result[main_key]:
              result[main_key][second_key] = {}
          result[main_key][second_key][third_key] = {'ODC元素值':value}
    return result

def preprocess_odc_config(odc_config):
    """修复第三层权重解析"""
    weights = {'layer2': [], 'layer3': {}}
    odc_elements = []
    
    for item in odc_config:
        if '权重' in item:
            weights['layer2'] = item['权重'].get('第二层权重', [])
            
            # 修复点：确保第三层权重是二维列表
            third_weights = item['权重'].get('第三层权重', [])
            if third_weights and not isinstance(third_weights[0], list):
                third_weights = [third_weights]  # 包装为二维列表
                
            for idx, sub_weights in enumerate(third_weights):
                weights['layer3'][idx] = sub_weights
        else:
            odc_elements.append(item)
    return weights, odc_elements

def calculate_score(node, current_path, odc_elements, weights, depth=1, parent_idx=None):
    """层级化权重计算"""
    # 末端节点处理
    if isinstance(node, dict) and 'ODC元素值' in node:
        element_name = current_path[-1]
        odc_conf = next((e for e in odc_elements if e['ODC元素'] == element_name), None)
        return normalize(odc_conf, node) if odc_conf else 1.0
    
    total = 0.0
    child_names = list(node.keys())
    
    # 动态获取权重
    if depth == 1:  # 主分类层
        layer_weights = weights['layer2']
    elif depth == 2:  # 第二层
        # 根据父节点在第二层的索引获取第三层权重
        layer_weights = weights['layer3'].get(parent_idx, [])
    else:
        layer_weights = []
    
    # 权重智能补齐（保持总和为1）
    sum_weights = sum(layer_weights)
    if len(child_names) > len(layer_weights):
        avg_weight = (1 - sum_weights) / (len(child_names) - len(layer_weights))
        layer_weights += [avg_weight] * (len(child_names) - len(layer_weights))
    else:
        layer_weights = layer_weights[:len(child_names)]
        sum_weights = sum(layer_weights)
        if sum_weights != 1:
            layer_weights = [w/sum_weights for w in layer_weights]
    
    # 递归计算
    for idx, (child_name, child_node) in enumerate(zip(child_names, node.values())):
        weight = layer_weights[idx] if idx < len(layer_weights) else 0.0
        score = calculate_score(
            child_node,
            current_path + [child_name],
            odc_elements,
            weights,
            depth + 1,
            parent_idx=idx if depth == 1 else parent_idx  # 传递第二层索引
        )
        total += score * weight
    
    return total

def compute_total_score(data_dict, odc_config):
    """入口函数"""
    weights, odc_elements = preprocess_odc_config(odc_config)
    main_category = next(iter(data_dict))
    return calculate_score(
        data_dict[main_category], 
        [main_category], 
        odc_elements, 
        weights, 
        depth=1
    )

def data_transfor_dict(all_api_data):  
  datalist = []
  for firstelment in all_api_data.keys():
    if firstelment in ['update_time','and_result'] :
      continue
    else:
      odc_element_data = build_nested_dict(all_api_data[firstelment]['detailed_info'][0])
      datalist.append(odc_element_data)
  return datalist

def Calculate_TTC(posx, posy, relvelx, relvely):
    relvel = np.sqrt( relvelx ** 2 +  relvely ** 2)
    distance = np.sqrt( posx ** 2 +  posy ** 2)
    TTC = distance / relvel
    # TTC_lon =  posx /  relvelx
    # TTC_lat =  posy /  relvely
    # return TTC_lon, TTC_lat
    return TTC

def RiskField(posx, posy, relvelx):
    A = 5.0
    kv = 0.5  # 调整为更小的值
    alpha = 0.2
    L_obs = 5.0
    # if not hasattr(Mainobstaclformation, 'relvelx') or not  launchstate:
    #     print("Mainobstaclformation 未初始化或无主目标")
    #     return 0.0
    sigma_v = kv * np.abs( relvelx)
    sigma_y = 20  # 调整为更小的值
    relv = -1 if  relvelx < 0 else 1
    numerator = A * np.exp(
        -( posx ** 2 / sigma_v ** 2) - ( posy ** 2 / (sigma_y ** 2)))
    denominator = 1 + np.exp(relv * ( posy - alpha * L_obs * relv))
    vehicle_risk = numerator / denominator
    return vehicle_risk

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

def risk_cal(all_api_data, all_odc_boundary, KEY_INDEX_MAP, w_map):
    datalist = data_transfor_dict(all_api_data)
    risklist = []
    for ODCdata in datalist:
        firstclassname = str(list(ODCdata)[0]) # 进入字典的第一大类
        index = leadto(KEY_INDEX_MAP, firstclassname)
        # print(index)
        odc_boundary = all_odc_boundary[index]
        # print(f'ODC大类名称:{firstclassname},对应的ODC边界:{odc_boundary}')
        risk_normalize = compute_total_score(ODCdata, odc_boundary)
        risklist.append({'ODC元素':firstclassname,'风险':risk_normalize})
        # print(f'ODC大类名称:{firstclassname},风险:{risk_normalize}')
    all_risk = 0
    for risk in risklist:
        w = leadto(w_map, risk['ODC元素'])
        all_risk += w * risk['风险']
    driving_risk = RiskField(posx, posy, relvelx)
    TTC = Calculate_TTC(posx, posy, relvelx, relvely)
    num_level, str_level = evaluate_risk(all_risk)
    driving_mode = select_driving_mode(all_risk, driving_risk)
    driving_mode = driving_mode.value
    return all_risk, risklist, driving_risk, TTC, num_level, str_level, driving_mode
