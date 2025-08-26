'''
控制驱动和制动系统报文解释器
支持ID: 0x0CCFE86A9
'''
from .base_parser import BaseParser

class Parser0CFE86A9(BaseParser):
    """
    解析 ID=0x0CCFE86A9 的控制驱动和制动系统报文数据
    周期: 20ms
    """
    def parse(self):
        """
        解析AS控制DCU数据
        :return: 解析后的数据字典，使用中文键名
        """
        try:
            data = [int(x, 16) for x in self.raw_data.split()]
            
            result = {
                "控制驱动和制动系统报文": {
                    # Byte0
                    "协同驾驶启动请求": self._parse_autod_req((data[0] >> 0) & 0x03),  # Bit0-1
                    "车辆纵向控制模式": self._parse_longit_ctrlmode((data[0] >> 2) & 0x03),  # Bit2-3
                    "紧急制动解除": self._parse_emergbrk_release((data[0] >> 4) & 0x03),  # Bit4-5
                    
                    # Byte1
                    "模拟加速踏板位置": self._parse_pedal_position(data[1]),  # Byte1
                    
                    # Byte2
                    "档位请求": self._parse_shift_req((data[2] >> 0) & 0x0F),  # Bit0-3
                    "P档位请求": self._parse_p_shift_req((data[2] >> 4) & 0x03),  # Bit4-5
                    
                    # Byte3
                    "模拟制动踏板位置": self._parse_pedal_position(data[3]),  # Byte3
                    
                    # Byte4
                    "自动驾驶车辆限速": self._parse_speed_limit(data[4]),  # Byte4
                    
                    # Byte7
                    "协同控制器生命帧": (data[7] >> 4) & 0x0F,  # Bit4-7
                }
            }
            
            return result
            
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}
    
    def _parse_autod_req(self, value):
        """解析协同驾驶启动请求"""
        states = {
            0: "未启动",
            1: "启动",
            2: "异常",
            3: "无效"
        }
        return states.get(value, "未知")
    
    def _parse_longit_ctrlmode(self, value):
        """解析车辆纵向控制模式"""
        states = {
            0: "无效",
            1: "踏板控制模式",
            2: "预留",
            3: "预留"
        }
        return states.get(value, "未知")
    
    def _parse_emergbrk_release(self, value):
        """解析紧急制动解除"""
        states = {
            0: "不解除",
            1: "立即解除",
            2: "预留",
            3: "预留"
        }
        return states.get(value, "未知")
    
    def _parse_pedal_position(self, value):
        """解析踏板位置
        分辨率: 0.4%/bit
        偏移量: 0
        范围: 0-250, 表示0%-100%
        示例:
        0x0A: 4%
        0xFE: 异常
        0xFF: 无效
        """
        if value == 0xFE:
            return "异常"
        elif value == 0xFF:
            return "无效"
        elif value > 250:
            return "超出范围"
        else:
            return f"{value * 0.4:.1f}%"
    
    def _parse_shift_req(self, value):
        """解析档位请求"""
        states = {
            0: "无效",
            1: "倒档R",
            2: "空档N",
            3: "前进档D",
            4: "预留",
            5: "预留",
            6: "预留",
            7: "预留"
        }
        return states.get(value, "未知")
    
    def _parse_p_shift_req(self, value):
        """解析P档位请求"""
        states = {
            0: "无效",
            1: "P档释放",
            2: "P档驻车",
            3: "预留"
        }
        return states.get(value, "未知")
    
    def _parse_speed_limit(self, value):
        """解析自动驾驶车辆限速
        分辨率: 1km/h/bit
        偏移量: 0
        范围: 5-100km/h
        示例:
        0x05: 5km/h
        0x0A: 10km/h
        注意: 初始化状态为0xFF
        """
        if value == 0xFF:
            return "初始化状态"
        elif 5 <= value <= 100:
            return f"{value}km/h"
        else:
            return "无效值" 