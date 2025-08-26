#zjg24
'''
车辆加速度信息解析器
支持ID: 0x00000215
'''
from .base_parser import BaseParser

class Parser0x00000215(BaseParser):
    """
    解析 ID=0x00000215 的车辆加速度信息数据
    """
    def parse(self):
        """
        解析车辆加速度信息数据
        :return: 解析后的数据字典，使用中文键名
        """
        try:
            data = [int(x, 16) for x in self.raw_data.split()]
            
            # 解析状态映射
            状态映射 = {
                0x00: "信号在规格限制内",
                0x01: "临时信号错误",
                0x02: "永久信号错误",
                0x03: "传感器元件初始化中"
            }
            
            # 解析各项数据
            内部错误 = "检测到内部处理错误" if data[1] & 0x01 else "无内部处理错误"
            电压错误 = "检测到过压/欠压" if (data[1] >> 1) & 0x01 else "无电压错误"
            
            # 获取各信号状态
            横摆信号状态 = 状态映射.get((data[1] >> 2) & 0x03, "未知状态")
            横向加速度状态 = 状态映射.get((data[1] >> 4) & 0x03, "未知状态")
            纵向加速度状态 = 状态映射.get((data[1] >> 6) & 0x03, "未知状态")
            
            return {
                "车辆加速度信息": {
                    "系统状态": {
                        "内部错误": 内部错误,
                        "电压状态": 电压错误,
                        "横摆信号状态": 横摆信号状态,
                        "横向加速度状态": 横向加速度状态,
                        "纵向加速度状态": 纵向加速度状态
                    },
                    "加速度数据": {
                        "纵向加速度": {
                            "数值": round(self._parse_axs_acceleration(data[2:4]), 2),
                            "单位": "m/s²"
                        },
                        "横向加速度": {
                            "数值": round(self._parse_ays_acceleration(data[4:6]), 2),
                            "单位": "m/s²"
                        },
                        "横摆角速度": {
                            "数值": round(self._parse_yrs_angular_speed(data[6:8]), 2),
                            "单位": "°/s"
                        }
                    },
                    "报文计数": data[5] & 0x0F
                }
            }
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}

    def _parse_axs_acceleration(self, bytes_data):
        """
        解析纵向加速度
        分辨率: 0.02m/s²/bit
        偏移量: -40.96
        """
        try:
            value = bytes_data[0] | (bytes_data[1] << 8)
            return (value * 0.02) - 40.96
        except Exception:
            return -40.96

    def _parse_ays_acceleration(self, bytes_data):
        """
        解析横向加速度
        分辨率: 0.02m/s²/bit
        偏移量: -40.96
        """
        try:
            value = bytes_data[0] | (bytes_data[1] << 8)
            return (value * 0.02) - 40.96
        except Exception:
            return -40.96

    def _parse_yrs_angular_speed(self, bytes_data):
        """
        解析横摆角速度
        分辨率: 0.08°/s/bit
        偏移量: -163.84
        """
        try:
            value = bytes_data[0] | (bytes_data[1] << 8)
            return (value * 0.08) - 163.84
        except Exception:
            return -163.84