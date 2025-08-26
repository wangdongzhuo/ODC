import numpy as np
Weather = np.array([
    [0.35, 0.7],   # clear
    [0.20, 0.2],   # cloudy
    [0.30, 0.05],  # rain
    [0.15, 0.05]   # fog
])

Lighting = np.array([
    [0.30, 0.7],   # daylight
    [0.10, 0.1],   # dawn/dusk
    [0.25, 0.1],   # dark-lighting
    [0.35, 0.1]    # dark
])

car_lane_status = np.array([
    [0.05, 0.7],   # 清晰可见
    [0.25, 0.2],   # 模糊
    [0.70, 0.1]    # 缺失
])

road_type = np.array([
    [0.20, 0.8],   # 快速路
    [0.80, 0.2]    # 其他类型
])

road_sign_instracture = np.array([
    [0.10, 0.9],   # 有标志
    [0.90, 0.1]    # 无标志
])

traffic_light = np.array([
    [0.10, 0.9],   # 有信号灯
    [0.90, 0.1]    # 无信号灯
])

PH = 0.03  # 碰撞先验概率
def calculate_p(conditions):
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
    P = (PXH0 * PH) / (PXH0 * PH + PXH1 * (1 - PH))
    return P
case1 = (
    0,       # rain
    0,      # dark
    2,          # 缺失
    0,     # 其他类型
    1,          # 无标志
    1          # 无信号灯（恶劣）
)
p1 = calculate_p(case1)
print(p1)

