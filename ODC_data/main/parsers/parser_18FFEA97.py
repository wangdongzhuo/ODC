'''
驱动状态报文解析器
支持ID: 0x18FFEA97
'''
from .base_parser import BaseParser

class Parser18FFEA97(BaseParser):
    """
    解析 ID=0x18FFEA97 的驱动状态报文数据
    周期: 20ms
    """
    def parse(self):
        """
        解析DCU反馈数据
        :return: 解析后的数据字典，使用中文键名
        """
        try:
            data = [int(x, 16) for x in self.raw_data.split()]
            
            result = {
                "驱动状态报文": {
                    "智能驾驶确认信号": self._parse_auto_drive_st((data[0] >> 0) & 0x03),  # Byte0 Bit0-1
                    "模拟加速踏板当前实际位置": self._parse_pedal_position(data[1]),  # Byte1
                    "模拟制动踏板当前实际位置": self._parse_pedal_position(data[2]),  # Byte2
                    "当前车速": self._parse_real_speed(data[5:7]),  # Byte5-6
                    "域控制器生命信号": (data[7] >> 2) & 0x3F,  # Byte7 Bit2-7
                }
            }
            
            return result
            
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}
    
    def _parse_auto_drive_st(self, value):
        """解析智能驾驶确认信号"""
        states = {
            0: "未启动",
            1: "确认已启动",
            2: "异常",
            3: "无效"
        }
        return states.get(value, "未知")
    
    def _parse_pedal_position(self, value):
        """解析踏板位置
        分辨率: 0.4%/bit
        偏移量: 0
        范围: 0-250, 表示0%-100%
        """
        if value == 0xFE:
            return "异常"
        elif value == 0xFF:
            return "无效"
        elif value > 250:
            return "超出范围"
        else:
            return f"{value * 0.4:.1f}%"
    
    def _parse_real_speed(self, data):
        """解析当前车速
        分辨率: 1/256(km/h)/bit
        偏移量: 0
        """
        speed = ((data[0] << 8) | data[1]) / 256.0
        return f"{speed:.2f}km/h"

