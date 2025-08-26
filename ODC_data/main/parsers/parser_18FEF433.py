#zjg20
'''
胎压监控系统状态解析器
支持ID: 0x18FEF433
'''
from .base_parser import BaseParser

class Parser18FEF433(BaseParser):
    """
    解析 ID=0x18FEF433 的胎压监控系统状态数据
    """
    def parse(self):
        """
        解析胎压监控系统状态数据
        :return: 解析后的数据字典，使用中文键名
        """
        try:
            data = [int(x, 16) for x in self.raw_data.split()]
            
            return {
                "胎压监控系统状态": {
                    "轮胎信息": {
                        "位置": self._parse_tire_location(data[0]),
                        "压力": {
                            "数值": self._parse_tire_pressure(data[1]),
                            "单位": "kPa"
                        },
                        "温度": {
                            "数值": self._parse_tire_temp(data[2:4]),
                            "单位": "°C"
                        }
                    },
                    "报警状态": {
                        "高温": self._parse_high_temp_alarm((data[4] >> 0) & 0x03),
                        "漏气": self._parse_leak_alarm((data[4] >> 2) & 0x03),
                        "信号丢失": self._parse_lost_alarm((data[4] >> 4) & 0x03),
                        "压力阈值": self._parse_valve_alarm(data[7] & 0x07)
                    }
                }
            }
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}

    def _parse_tire_location(self, byte_data):
        """解析轮胎定位"""
        location_map = {
            0x00: "轴1 前1",
            0x01: "轴1 前2",
            0x10: "轴2 前1",
            0x11: "轴2 前2",
            0x12: "轴2 前3",
            0x13: "轴2 前4",
            0x20: "轴3 前1",
            0x21: "轴3 前2",
            0x60: "备胎1",
            0x61: "备胎2"
        }
        return location_map.get(byte_data, "未知位置")

    def _parse_tire_pressure(self, byte_data):
        """
        解析轮胎压力
        分辨率: 4 kPa/bit
        范围: 0-1020 kPa
        """
        try:
            pressure = byte_data * 4
            if 0 <= pressure <= 1020:
                return round(pressure, 1)
            return 0
        except Exception:
            return 0

    def _parse_tire_temp(self, bytes_data):
        """
        解析轮胎温度
        分辨率: 0.03125 °C/bit
        偏移量: -273 °C
        范围: -273-1735 °C
        """
        try:
            value = bytes_data[0] | (bytes_data[1] << 8)
            temp = (value * 0.03125) - 273
            
            if -273 <= temp <= 1735:
                return round(temp, 1)
            return 0.0
        except Exception:
            return 0.0

    def _parse_high_temp_alarm(self, value):
        """解析轮胎高温报警"""
        status_map = {
            0x00: "正常",
            0x01: "高温报警",
            0x02: "预留",
            0x03: "预留"
        }
        return status_map.get(value, "未知状态")

    def _parse_leak_alarm(self, value):
        """解析轮胎漏气报警"""
        status_map = {
            0x00: "正常",
            0x01: "轮胎漏气",
            0x02: "预留",
            0x03: "预留"
        }
        return status_map.get(value, "未知状态")

    def _parse_lost_alarm(self, value):
        """解析轮胎信号丢失报警"""
        status_map = {
            0x00: "正常",
            0x01: "传感器掉报警",
            0x02: "预留",
            0x03: "预留"
        }
        return status_map.get(value, "未知状态")

    def _parse_valve_alarm(self, value):
        """解析轮胎压力阈值报警"""
        status_map = {
            0x00: "超出极限压力",
            0x01: "过压",
            0x02: "没有压力报警",
            0x03: "压力过低",
            0x04: "低于最低极限",
            0x05: "无效值",
            0x06: "未示意错误"
        }
        return status_map.get(value, "未知状态") 