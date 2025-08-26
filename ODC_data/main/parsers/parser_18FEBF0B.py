#zjg19
'''
轮速报文解析器
支持ID: 0x18FEBF0B
'''
from .base_parser import BaseParser

class Parser18FEBF0B(BaseParser):
    """
    解析 ID=0x18FEBF0B 的轮速报文数据
    """
    def parse(self):
        """
        解析轮速数据
        :return: 解析后的数据字典，使用中文键名
        """
        try:
            data = [int(x, 16) for x in self.raw_data.split()]
            
            return {
                "轮速报文": {
                    "前轴速度": {
                        "数值": round(self._parse_steer_axle_speed(data[0:2]), 3),
                        "单位": "km/h"
                    },
                    "相对速度": {
                        "前轴左轮": {
                            "数值": round(self._parse_relative_speed(data[2]), 4),
                            "单位": "km/h"
                        },
                        "前轴右轮": {
                            "数值": round(self._parse_relative_speed(data[3]), 4),
                            "单位": "km/h"
                        },
                        "第二轴左轮": {
                            "数值": round(self._parse_relative_speed(data[4]), 4),
                            "单位": "km/h"
                        },
                        "第二轴右轮": {
                            "数值": round(self._parse_relative_speed(data[5]), 4),
                            "单位": "km/h"
                        },
                        "第三轴左轮": {
                            "数值": round(self._parse_relative_speed(data[6]), 4),
                            "单位": "km/h"
                        },
                        "第三轴右轮": {
                            "数值": round(self._parse_relative_speed(data[7]), 4),
                            "单位": "km/h"
                        }
                    }
                }
            }
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}

    def _parse_steer_axle_speed(self, bytes_data):
        """
        解析前轴速度
        分辨率: 1/256 km/h/bit
        范围: 0-250.996 km/h
        """
        try:
            # 将2个字节组合成16位整数
            value = bytes_data[0] | (bytes_data[1] << 8)
            
            # 按照1/256 km/h/bit计算实际速度
            speed = value / 256.0
            
            # 确保速度在有效范围内
            if 0 <= speed <= 250.996:
                return speed
            return 0.0
        except Exception:
            return 0.0

    def _parse_relative_speed(self, byte_data):
        """
        解析相对速度
        分辨率: 1/16 km/h/bit
        偏移量: -7.8125 km/h
        范围: (-7.8125) - (+7.8125) km/h
        """
        try:
            # 将8位数据转换为相对速度
            rel_speed = (byte_data / 16.0) - 7.8125
            
            # 确保速度在有效范围内
            if -7.8125 <= rel_speed <= 7.8125:
                return rel_speed
            return 0.0
        except Exception:
            return 0.0 