#zjg17
'''
BC智能车辆状态反馈解析器
'''
from .base_parser import BaseParser

class Parser18FA1117(BaseParser):
    """
    解析 ID=0x18FA1117 的 BC智能车辆状态反馈数据
    """
    def parse(self):
        """
        解析 BC智能车辆状态反馈
        :return: 解析后的数据字典，使用中文键名
        """
        try:
            data = [int(x, 16) for x in self.raw_data.split()]
            
            return {
                "智能车辆状态反馈": {
                    "数据包信息": {
                        "包号": self._parse_data_package(data[0] & 0x03)
                    },
                    "车门状态": {
                        "前门": self._parse_door_status((data[1] >> 2) & 0x07),
                        "中门": self._parse_door_status((data[1] >> 5) & 0x07),
                        "后门钥匙": self._parse_light_status((data[5] >> 6) & 0x03)
                    },
                    "灯光状态": {
                        "倒车灯": self._parse_reversing_light((data[1] >> 0) & 0x03),
                        "制动灯": self._parse_light_status((data[2] >> 0) & 0x03),
                        "日间行车灯1": self._parse_light_status((data[3] >> 0) & 0x03),
                        "日间行车灯2": self._parse_light_status((data[2] >> 2) & 0x03),
                        "前雾灯": self._parse_light_status((data[3] >> 2) & 0x03),
                        "后雾灯": self._parse_light_status((data[3] >> 4) & 0x03),
                        "远光灯": self._parse_light_status((data[3] >> 6) & 0x03),
                        "近光灯": self._parse_light_status((data[4] >> 0) & 0x03),
                        "右转向灯": self._parse_light_status((data[4] >> 2) & 0x03),
                        "左转向灯": self._parse_light_status((data[4] >> 4) & 0x03),
                        "行车灯": self._parse_light_status((data[4] >> 6) & 0x03),
                        "示廓灯": self._parse_light_status((data[5] >> 0) & 0x03),
                        "顶灯": self._parse_light_status((data[6] >> 0) & 0x03)
                    },
                    "报警状态": {
                        "制动油液位": self._parse_alarm_status((data[2] >> 4) & 0x03),
                        "冷却液位": self._parse_alarm_status((data[6] >> 2) & 0x03),
                        "紧急使能": self._parse_alarm_status((data[6] >> 4) & 0x03),
                        "制动摩擦片": self._parse_alarm_status((data[6] >> 6) & 0x03),
                        "紧急门开关": self._parse_alarm_status((data[7] >> 3) & 0x03)
                    },
                    "其他状态": {
                        "喇叭": self._parse_light_status((data[2] >> 6) & 0x03),
                        "雨刮": self._parse_wiper_status((data[7] >> 0) & 0x03)
                    }
                }
            }
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}

    def _parse_data_package(self, value):
        """解析数据包号"""
        status_map = {
            0x00: "无意义",
            0x01: "第1号数据包",
            0x02: "第2号数据包",
            0x03: "第3号数据包"
        }
        return status_map.get(value, "未知状态")

    def _parse_reversing_light(self, value):
        """解析倒车灯状态"""
        status_map = {
            0x00: "关闭",
            0x01: "开启"
        }
        return status_map.get(value, "预留")

    def _parse_door_status(self, value):
        """解析门状态"""
        status_map = {
            0x00: "门正在关闭过程",
            0x01: "门已经开",
            0x02: "门已经关",
            0x03: "门正在开启过程",
            0x04: "门正在关闭过程"
        }
        return status_map.get(value, "预留")

    def _parse_light_status(self, value):
        """解析灯光状态"""
        status_map = {
            0x00: "关闭",
            0x01: "开启"
        }
        return status_map.get(value, "预留")

    def _parse_alarm_status(self, value):
        """解析报警状态"""
        status_map = {
            0x00: "未报警",
            0x01: "报警"
        }
        return status_map.get(value, "预留")

    def _parse_wiper_status(self, value):
        """解析雨刮状态"""
        status_map = {
            0x00: "关闭",
            0x01: "间歇",
            0x02: "低速",
            0x03: "高速"
        }
        return status_map.get(value, "未知状态") 