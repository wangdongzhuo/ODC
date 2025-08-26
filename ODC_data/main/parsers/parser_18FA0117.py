#zjg 15
'''
BC智能控制状态反馈解析器
'''
from .base_parser import BaseParser

class Parser18FA0117(BaseParser):
    """
    解析 ID=0x18FA0117 的 BC智能控制状态反馈数据
    """
    def parse(self):
        """
        解析 BC智能控制状态反馈
        :return: 解析后的数据字典，使用中文键名
        """
        try:
            data = [int(x, 16) for x in self.raw_data.split()]
            
            return {
                "智能控制状态反馈": {
                    "按键状态": {
                        "紧急危险": self._parse_emergence_key(data[0] & 0x03),
                        "屏蔽智能驾驶": self._parse_auto_door_key((data[0] >> 2) & 0x03),
                        "启动": self._parse_start_key((data[0] >> 4) & 0x03),
                        "车内前门": self._parse_in_front_door_key((data[2] >> 6) & 0x03),
                        "车外前门": self._parse_door_key(data[3] & 0x03),
                        "喇叭": self._parse_horn_key((data[3] >> 6) & 0x03),
                        "车内中门": self._parse_door_key(data[5] & 0x03),
                        "车外中门": self._parse_door_key((data[5] >> 2) & 0x03),
                        "车内后门": self._parse_door_key((data[5] >> 4) & 0x03),
                        "车外后门": self._parse_door_key((data[5] >> 6) & 0x03)
                    },
                    "报警状态": {
                        "安全带": self._parse_safety_belt_alarm(data[1] & 0x03),
                        "司机离座": self._parse_driver_left_alarm((data[1] >> 2) & 0x03)
                    },
                    "车辆状态": {
                        "除霜": self._parse_defrosting((data[4] >> 4) & 0x03),
                        "危险警告": self._parse_hazard_warning(data[4] >> 6)
                    }
                }
            }
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}

    def _parse_emergence_key(self, value):
        """紧急危险按键状态"""
        status_map = {
            0x00: "未激活",
            0x01: "激活"
        }
        return status_map.get(value, "预留")

    def _parse_auto_door_key(self, value):
        """屏蔽智能驾驶按键状态"""
        status_map = {
            0x00: "未激活",
            0x01: "激活"
        }
        return status_map.get(value, "预留")

    def _parse_start_key(self, value):
        """启动按键状态"""
        status_map = {
            0x00: "未激活",
            0x01: "ON档",
            0x02: "START档",
            0x03: "ACC档"
        }
        return status_map.get(value, "未知状态")

    def _parse_safety_belt_alarm(self, value):
        """司机安全带未系报警"""
        status_map = {
            0x00: "未激活",
            0x01: "激活"
        }
        return status_map.get(value, "预留")

    def _parse_driver_left_alarm(self, value):
        """司机离座报警"""
        status_map = {
            0x00: "未激活",
            0x01: "激活"
        }
        return status_map.get(value, "预留")

    def _parse_in_front_door_key(self, value):
        """车内前门按键状态"""
        status_map = {
            0x00: "未激活",
            0x01: "激活开门",
            0x02: "激活关门"
        }
        return status_map.get(value, "预留")

    def _parse_door_key(self, value):
        """门控制按键状态(通用)"""
        status_map = {
            0x00: "未激活",
            0x01: "激活"
        }
        return status_map.get(value, "预留")

    def _parse_horn_key(self, value):
        """喇叭按键状态"""
        status_map = {
            0x00: "未激活",
            0x01: "激活",
            0x02: "无效"
        }
        return status_map.get(value, "预留")

    def _parse_defrosting(self, value):
        """除霜状态"""
        status_map = {
            0x00: "未输出",
            0x01: "低档输出",
            0x02: "高档输出",
            0x03: "无效"
        }
        return status_map.get(value, "未知状态")

    def _parse_hazard_warning(self, value):
        """危险警告信号按键状态"""
        status_map = {
            0x00: "未激活",
            0x01: "激活"
        }
        return status_map.get(value, "预留")