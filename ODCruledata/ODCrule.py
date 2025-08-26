import re
from ODCruledata.ODCboundary import ODC
def in_range(min_value, max_value):
    """范围检查函数"""
    return lambda x: min_value <= x <= max_value

def is_in_list(allowed_values):
    """是否在预定义列表中检查函数"""
    return lambda x: x in allowed_values

def is_true(x):
    """检查是否为 True"""
    return x is True

def is_false(x):
    """检查是否为 False"""
    return x is False


# 创建验证规则映射,此处的规则后面还要修正，依据测试得到
pre_communica_rules = {
    '丢包率':[in_range(ODC["通讯与计算"]["丢包率"][""]["value"][0],ODC["通讯与计算"]["丢包率"][""]["value"][1])],
    '通信模式':[is_in_list(ODC["通讯与计算"]["通信模式"][""]["value"])],
    '通信时延':[in_range(0,60)],
    # '协同自适应巡航':[in_range(ODC["通讯与计算"]["通信时延"]["协同自适应巡航"]["value"][0],ODC["通讯与计算"]["通信时延"]["协同自适应巡航"]["value"][1])],
    # '无信号匝道的转向或交替通行':[in_range(ODC["通讯与计算"]["通信时延"]["无信号匝道的转向或交替通行"]["value"][0],ODC["通讯与计算"]["通信时延"]["无信号匝道的转向或交替通行"]["value"][1])],
    # '协作式变道':[in_range(ODC["通讯与计算"]["通信时延"]["协作式变道"]["value"][0],ODC["通讯与计算"]["通信时延"]["协作式变道"]["value"][1])],
    # '路口对向行驶车辆的无保护左转':[in_range(ODC["通讯与计算"]["通信时延"]["路口对向行驶车辆的无保护左转"]["value"][0],ODC["通讯与计算"]["通信时延"]["路口对向行驶车辆的无保护左转"]["value"][1])],
    # '协作式车道汇入':[in_range(ODC["通讯与计算"]["通信时延"]["协作式车道汇入"]["value"][0],ODC["通讯与计算"]["通信时延"]["协作式车道汇入"]["value"][1])],
    # '编队行驶':[in_range(ODC["通讯与计算"]["通信时延"]["编队行驶"]["value"][0],ODC["通讯与计算"]["通信时延"]["编队行驶"]["value"][1])],
    # '动态车速限制':[in_range(ODC["通讯与计算"]["通信时延"]["动态车速限制"]["value"][0],ODC["通讯与计算"]["通信时延"]["动态车速限制"]["value"][1])],
    # '远程控制驾驶':[in_range(ODC["通讯与计算"]["通信时延"]["远程控制驾驶"]["value"][0],ODC["通讯与计算"]["通信时延"]["远程控制驾驶"]["value"][1])],
}

pre_digtal_info_rule_rules = {
    '消息体':[is_true],
    # '信源发送频率':[is_true],
}

pre_driver_rules = {
    '注意力状态':[is_true],
    '安全带状态':[is_true],
    '位姿状态':[is_true],
}

pre_map_local_rules = {
    '地图':[is_true],
    '定位系统':[is_in_list(ODC["地图与定位"]["定位系统"][""]["value"])],
}

pre_object_rules = {
    '目标物类型':[is_in_list(ODC["目标物"]["目标物类型"][""]["value"])],
}

pre_road_rules = {
    '区域':[is_in_list(ODC["道路属性"]["道路类型"]["区域"]["value"])],
    '城市道路':[is_in_list(ODC["道路属性"]["道路类型"]["城市道路"]["value"])],
    '高速公路':[is_in_list(ODC["道路属性"]["道路类型"]["高速公路"]["value"])],
    '乡村道路':[is_false],
    '道路表面状况':[is_in_list(ODC["道路属性"]["道路表面"]["道路表面状况"]["value"])],
    '纵断面坡度':[in_range(ODC["道路属性"]["道路几何"]["纵断面坡度"]["value"][0],ODC["道路属性"]["道路几何"]["纵断面坡度"]["value"][1])],
    '道路曲率半径':[in_range(ODC["道路属性"]["道路几何"]["道路曲率半径"]["value"][0],ODC["道路属性"]["道路几何"]["道路曲率半径"]["value"][1])],
    '道路交叉':[is_in_list(ODC["道路属性"]["道路几何"]["道路交叉"]["value"])],
    '标线质量':[in_range(ODC["道路属性"]["车道特征"]["标线质量"]["value"][0],ODC["道路属性"]["车道特征"]["标线质量"]["value"][1])],
    '车道状态':[is_true],
    '车道宽度':[in_range(ODC["道路属性"]["车道特征"]["车道宽度"]["value"][0],ODC["道路属性"]["车道特征"]["车道宽度"]["value"][1])],
    '车道标线颜色':[is_in_list(ODC["道路属性"]["车道特征"]["车道标线颜色"]["value"])],
    '车道类型':[is_in_list(ODC["道路属性"]["车道特征"]["车道类型"]["value"])],
    '车道数量':[in_range(ODC["道路属性"]["车道特征"]["车道数量"]["value"][0],ODC["道路属性"]["车道特征"]["车道数量"]["value"][1])],
}

pre_road_infrustrction_rules = {
    '交通标志':[is_true],
    '交通信号灯':[is_true],
    '智能路侧设施':[in_range(ODC["道路设施"]["智能路侧设施"][""]["value"][0],ODC["道路设施"]["智能路侧设施"][""]["value"][1])],
    '特殊设施':[is_in_list(ODC["道路设施"]["特殊设施"][""]["value"])]
}

pre_tran_condi_rules = {
    '交通事件':[is_false],
    '交通拥堵度':[is_in_list(ODC["交通条件"]["交通拥堵度"][""]["value"])],
    '可协作车辆':[is_true],
    '交通法规':[is_true],
}

pre_vehicle_rules = {
    # '前向防撞功能':is_true,
    '协同驾驶状态':is_true,
    'LKA功能':is_true,
    'ACC功能':is_true,
    'AEB功能':is_true,
    # '车速':in_range(ODC["车辆状态"]["车辆运动状态"]["车速"]["value"][0], ODC["车辆状态"]["车辆运动状态"]["车速"]["value"][1]),
    # '前向距离':in_range(ODC["车辆状态"]["车辆运动状态"]["前向距离"]["value"][0], ODC["车辆状态"]["车辆运动状态"]["前向距离"]["value"][1]),
    # '纵向加速度':in_range(ODC["车辆状态"]["车辆运动状态"]["纵向加速度"]["value"][0], ODC["车辆状态"]["车辆运动状态"]["纵向加速度"]["value"][1]),
    # '横向加速度':in_range(ODC["车辆状态"]["车辆运动状态"]["横向加速度"]["value"][0], ODC["车辆状态"]["车辆运动状态"]["横向加速度"]["value"][1]),
    # '垂向加速度':in_range(ODC["车辆状态"]["车辆运动状态"]["垂向加速度"]["value"][0], ODC["车辆状态"]["车辆运动状态"]["垂向加速度"]["value"][1]),
    # '横摆角速度':in_range(ODC["车辆状态"]["车辆运动状态"]["横摆角速度"]["value"][0], ODC["车辆状态"]["车辆运动状态"]["横摆角速度"]["value"][1]),
    # '方向盘转角':in_range(ODC["车辆状态"]["车辆运动状态"]["方向盘转角"]["value"][0], ODC["车辆状态"]["车辆运动状态"]["方向盘转角"]["value"][1]),
    '车速':in_range(0,60),
    '前向距离':in_range(0, 60),
    # '纵向加速度':in_range(0, 60),
    '横向加速度':in_range(0, 60),
    '垂向加速度':in_range(0, 60),
    '横摆角速度':in_range(0, 60),
    '方向盘转角':in_range(0, 60),
    '前向碰撞预警':is_true,
    '异常车辆预警':is_true,
    '紧急车辆预警':is_true,
    'GNSS状态':is_true,
    '域控状态':is_true,
    '总线状态':is_true,
    '以太网状态':is_true,
    '传感器状态':is_true, 
    '计算平台状态':is_true, 
    '硬件状态':is_true, 
    '系统状态':is_true, 
    '档位':is_true, 
    '刹车':is_true, 
    '电子手刹':is_true, 
    '油门开度':in_range(ODC["车辆状态"]["系统控制状态"]["油门开度"]["value"][0], ODC["车辆状态"]["系统控制状态"]["油门开度"]["value"][1]), 
    '转向灯关闭':is_true,
    '车辆模式':is_in_list([ODC["车辆状态"]["系统控制状态"]["车辆模式"]["value"]]), 
    '前雨刮器':is_true, 
    '车门状态':is_true, 
}

pre_weather_rules = {
    '风':[in_range(ODC["环境条件"]["天气条件"]["风"]["value"][0], ODC["环境条件"]["天气条件"]["风"]["value"][1])],
    '雪':[is_false],
    '雨':[in_range(ODC["环境条件"]["天气条件"]["雨"]["value"][0], ODC["环境条件"]["天气条件"]["雨"]["value"][1])],
    '气温':[in_range(ODC["环境条件"]["气温"][""]["value"][0], ODC["环境条件"]["气温"][""]["value"][1])],
    '雾霾':[in_range(ODC["环境条件"]["颗粒物"]["雾霾"]["value"][0], ODC["环境条件"]["颗粒物"]["雾霾"]["value"][1])],
    '光照条件':[is_in_list([ODC["环境条件"]["光照条件"][""]["value"]])],
}