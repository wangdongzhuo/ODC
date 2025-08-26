'''
域控制器基础信息2报文解析器
支持ID: 0x18FF7097
'''
from .base_parser import BaseParser

class Parser18FF7097(BaseParser):
    """
    解析 ID=0x18FF7097 的域控制器基础信息2报文数据
    周期: 100ms
    """
    def parse(self):
        """
        解析域控制器基础信息2数据
        :return: 解析后的数据字典，使用中文键名
        """
        try:
            data = [int(x, 16) for x in self.raw_data.split()]
            
            result = {
                "域控制器基础信息2": {
                    "限制进入自动驾驶原因": self._parse_autod_limitin_reason(data[0]),  # Byte0
                    "紧急停车激活原因": self._parse_emergency_stop_reason((data[2] >> 0) & 0x07),  # Byte2 Bit0-2
                    "低压系统故障": self._parse_sys_low_fault((data[2] >> 3) & 0x07),  # Byte2 Bit3-5
                    "驾驶员接管提醒": self._parse_driver_takeover_req((data[2] >> 6) & 0x03),  # Byte2 Bit6-7
                    "车辆驾驶模式": self._parse_vehicle_drive_mode((data[3] >> 3) & 0x07),  # Byte3 Bit3-5
                    "退出自动驾驶原因": self._parse_autod_out_reason(data[4]),  # Byte4
                    "限制手动驾驶原因": self._parse_manual_limitin_reason((data[5] >> 0) & 0x0F),  # Byte5 Bit0-3
                    "ABS激活状态": self._parse_abs_active_st((data[6] >> 0) & 0x03),  # Byte6 Bit0-1
                    "制动系统故障": self._parse_brake_sys_fault((data[6] >> 2) & 0x03),  # Byte6 Bit2-3
                    "整车机械制动状态": self._parse_brake_st((data[6] >> 4) & 0x03),  # Byte6 Bit4-5
                    "高压系统故障": self._parse_sys_high_fault((data[7] >> 0) & 0x07),  # Byte7 Bit0-2
                    "启动按键状态": self._parse_start_key_st((data[7] >> 6) & 0x03),  # Byte7 Bit6-7
                }
            }
            
            return result
            
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}
    
    def _parse_autod_limitin_reason(self, value):
        """解析限制进入自动驾驶原因"""
        states = {
            0: "无",
            1: "急停按键触发",
            2: "远程停车按键激活",
            3: "前碰撞触发",
            4: "后碰撞触发",
            5: "绞盘按键触发",
            6: "智能驾驶按键未切换",
            7: "智能驾驶按键未允许",
            8: "机械档位不满足",
            9: "制动踏板不满足",
            10: "油门踏板不满足",
            11: "转向系统模式不满足",
            12: "方向盘实际角度不满足",
            13: "车辆驻车状态不满足",
            14: "驻车按键触发",
            15: "车速不满足",
            16: "高压未上电成功",
            17: "自检不满足",
            18: "低压系统故障",
            19: "绞刹手柄不满足",
            20: "遥控手柄按管",
            21: "智能系统掉线",
            22: "档位请求不满足",
            23: "制动请求不满足",
            24: "油门请求不满足",
            25: "方向盘角度请求不满足",
            26: "智能驾驶命令未切换",
            27: "智能系统未启动",
            28: "智能系统启动时间间隔不满足",
            29: "智能停车未允许按钮",
            30: "安全带未系",
            31: "可机器人",
            32: "门未关闭"
        }
        return states.get(value, "未知")
    
    def _parse_emergency_stop_reason(self, value):
        """解析紧急停车激活原因"""
        states = {
            0: "无",
            1: "紧急停车开关",
            2: "远程急停",
            3: "急停开关3",
            4: "急停开关4",
            5: "前碰撞触发",
            6: "后碰撞触发",
            7: "预留"
        }
        return states.get(value, "未知")
    
    def _parse_sys_low_fault(self, value):
        """解析低压系统故障"""
        states = {
            0: "无故障",
            1: "一级故障",
            2: "二级故障",
            3: "三级故障",
            4: "预留",
            5: "预留",
            6: "预留",
            7: "预留"
        }
        return states.get(value, "未知")
    
    def _parse_driver_takeover_req(self, value):
        """解析驾驶员接管提醒"""
        states = {
            0: "未激活",
            1: "激活提醒",
            2: "预留",
            3: "预留"
        }
        return states.get(value, "未知")
    
    def _parse_vehicle_drive_mode(self, value):
        """解析车辆驾驶模式"""
        states = {
            0: "无",
            1: "紧急制动模式",
            2: "手动模式",
            3: "预留",
            4: "自动驾驶模式",
            5: "蠕行模式",
            6: "自检模式",
            7: "远程驾驶模式"
        }
        return states.get(value, "未知")
    
    def _parse_autod_out_reason(self, value):
        """解析退出自动驾驶原因"""
        states = {
            0: "无",
            1: "急停按键触发",
            2: "远程停车按键激活",
            3: "前碰撞触发",
            4: "后碰撞触发",
            5: "绞盘按键触发",
            6: "智能驾驶按键未允许",
            7: "可机操作机械档位",
            8: "可机踩制动踏板",
            9: "可机踩油门踏板",
            10: "可机接管方向盘",
            11: "可机操作驻车按键",
            12: "高压下电且停车",
            13: "低压严重故障且停车",
            14: "可机操作绞刹手柄",
            15: "手术器手按管",
            16: "智能系统掉线",
            17: "智能系统退出",
            18: "转向系统模式不满足"
        }
        return states.get(value, "未知")
    
    def _parse_manual_limitin_reason(self, value):
        """解析限制手动驾驶原因"""
        states = {
            0: "无",
            1: "紧急制动模式激活",
            2: "绞刹模式激活",
            3: "自检未结束",
            4: "绞刹按键激活",
            5: "智能驾驶按键未允许",
            6: "档位移除",
            7: "车速不满足",
            8: "高压未上电成功",
            9: "智能停车未允许按管",
            10: "其他"
        }
        return states.get(value, "未知")
    
    def _parse_abs_active_st(self, value):
        """解析ABS激活状态"""
        states = {
            0: "未激活",
            1: "激活",
            2: "无效",
            3: "无效"
        }
        return states.get(value, "未知")
    
    def _parse_brake_sys_fault(self, value):
        """解析制动系统故障"""
        states = {
            0: "无故障",
            1: "一级故障",
            2: "二级故障",
            3: "三级故障"
        }
        return states.get(value, "未知")
    
    def _parse_brake_st(self, value):
        """解析整车机械制动状态"""
        states = {
            0: "未工作",
            1: "工作中",
            2: "无效",
            3: "无效"
        }
        return states.get(value, "未知")
    
    def _parse_sys_high_fault(self, value):
        """解析高压系统故障"""
        states = {
            0: "无故障",
            1: "一级故障",
            2: "二级故障",
            3: "三级故障",
            4: "四级故障",
            5: "无效",
            6: "无效",
            7: "无效"
        }
        return states.get(value, "未知")
    
    def _parse_start_key_st(self, value):
        """解析启动按键状态"""
        states = {
            0: "未激活",
            1: "ON档",
            2: "START档",
            3: "ACC档"
        }
        return states.get(value, "未知")


