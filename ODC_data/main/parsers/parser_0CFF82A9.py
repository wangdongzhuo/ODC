'''
AS控制L2系统报文解析器
支持ID: 0x0CFF84A9
'''
from .base_parser import BaseParser

class Parser0CFF82A9(BaseParser):
    """
    解析 ID=0x0CFF84A9 的AS控制L2系统报文数据
    周期: 20ms
    """
    def parse(self):
        """
        解析AS控制L2系统数据
        :return: 解析后的数据字典，使用中文键名
        """
        try:
            data = [int(x, 16) for x in self.raw_data.split()]

            result = {
                "AS控制L2系统报文": {
                    "LKA功能开启请求": self._parse_lka_ctrl_req((data[0] >> 0) & 0x03),  # Byte0 Bit0-1
                    "ACC功能开启请求": self._parse_acc_ctrl_req((data[0] >> 2) & 0x03),  # Byte0 Bit2-3
                    "ACC激活请求": self._parse_acc_active_req((data[1] >> 0) & 0x03),  # Byte1 Bit0-1
                    "协同控制器生命帧": (data[1] >> 4) & 0x0F,  # Byte1 Bit4-7
                    "协同控制器请求设定巡航车速": data[3]  # Byte3, 单位km/h
                }
            }

            return result

        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}

    def _parse_lka_ctrl_req(self, value):
        """解析LKA功能开启请求"""
        states = {
            0: "未请求",
            1: "LKA功能开启请求",
            2: "LKA功能关闭请求",
            3: "预留"
        }
        return states.get(value, "未知")

    def _parse_acc_ctrl_req(self, value):
        """解析ACC功能开启请求"""
        states = {
            0: "未请求",
            1: "ACC功能开启请求",
            2: "ACC功能关闭请求",
            3: "预留"
        }
        return states.get(value, "未知")

    def _parse_acc_active_req(self, value):
        """解析ACC激活请求"""
        states = {
            0: "未请求",
            1: "ACC激活请求",
            2: "无效",
            3: "无效"
        }
        return states.get(value, "未知")

