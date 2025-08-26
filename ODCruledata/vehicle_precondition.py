# 域控基础信息1
def check_gear_state(gear_state):
    return gear_state == "释放"

def check_current_gear(current_gear):
    return current_gear == "预留"

def check_high_voltage_status(high_voltage_status):
    return high_voltage_status == "无效"

def check_power_steering_status(power_steering_status):
    return power_steering_status == "熄灭"

# 创建验证函数来验证整个“域控制器基础信息报文”

def validate_yukong(data):
    # 获取消息中的 data 部分
    data_field = data
    
    # 对每个字段进行验证
    is_gear_state_valid = check_gear_state(data_field["当前P档位状态"])
    is_current_gear_valid = check_current_gear(data_field["当前档位"])
    is_high_voltage_status_valid = check_high_voltage_status(data_field["车辆当前高压驱动状态"])
    is_power_steering_status_valid = check_power_steering_status(data_field["转向助力油泵状态"])
    
    # 汇总所有验证结果
    if is_gear_state_valid and is_current_gear_valid and is_high_voltage_status_valid and is_power_steering_status_valid:
        return True
    else:
        return False

# 胎压监控系统状态

# 定义各字段的验证函数

def check_signal_loss(signal_loss):
    return signal_loss == "正常"

def check_pressure_threshold(pressure_threshold):
    return pressure_threshold == "未示意错误"

def check_leakage(leakage):
    return leakage == "正常"

def check_high_temperature(high_temperature):
    return high_temperature == "正常"

# 创建验证函数来验证整个“胎压监控系统状态”

def validate_taiya(data):
    # 获取消息中的 data 部分
    data_field = data
    
    # 对每个字段进行验证
    is_signal_loss_valid = check_signal_loss(data_field["报警状态"]["信号丢失"])
    is_pressure_threshold_valid = check_pressure_threshold(data_field["报警状态"]["压力阈值"])
    is_leakage_valid = check_leakage(data_field["报警状态"]["漏气"])
    is_high_temperature_valid = check_high_temperature(data_field["报警状态"]["高温"])
    
    # 汇总所有验证结果
    if is_signal_loss_valid and is_pressure_threshold_valid and is_leakage_valid and is_high_temperature_valid:
        return True
    else:
        return False
    
    #域控基础信息2

def check_low_voltage(gear_state):
    return gear_state == "无故障"

def check_high_voltage(current_gear):
    return current_gear == "无故障"

def check_break_status(high_voltage_status):
    return high_voltage_status == "无故障"

def check_start_button_status(power_steering_status):
    return power_steering_status == "START档"


def validate_yukong2(data):
    # 获取消息中的 data 部分
    data_field = data
    
    # 对每个字段进行验证
    is_low_voltage_valid = check_low_voltage(data_field["低压系统故障"])
    is_high_voltage_valid = check_high_voltage(data_field["高压系统故障"])
    is_break_status_valid = check_break_status(data_field["制动系统故障"])
    is_start_button_valid = check_start_button_status(data_field["启动按键状态"])
    
    # 汇总所有验证结果
    if is_low_voltage_valid and is_high_voltage_valid and is_start_button_valid and is_break_status_valid:
        return True
    else:
        return False

