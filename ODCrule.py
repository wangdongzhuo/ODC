import re
def in_range(min_value, max_value):
    """范围检查函数"""
    return lambda x: min_value <= x <= max_value

def equals(value):
    """等于检查函数"""
    return lambda x: x == value

def matches_pattern(pattern):
    """正则表达式匹配检查函数"""
    return lambda x: bool(re.match(pattern, x))

def is_in_list(allowed_values):
    """是否在预定义列表中检查函数"""
    return lambda x: x in allowed_values

def is_true(value):
    return value is True

# 创建验证规则映射
pre_vehicle_rules = {
    '档位满足要求': [is_true],
    '手刹松开': [is_true],
    '刹车踏板压力小于阈值': [is_true],
    '油门开度': [in_range(0, 60)],
    '车辆模式': [is_in_list(["ACC","LKA","CMS"])],
    '雨刮器处于关闭或抵挡状态': [is_true],
    '车门关闭': [is_true],
    '转向灯未开启': [is_true],
    '整车域控故障状态': [is_true],
    '传感器故障': [is_true],
    '协同驾驶硬件故障状态': [is_true],
    '自动驾驶系统故障状态': [is_true],
}