'''
支持ID: 0x18FF82A9
'''
from .base_parser import BaseParser

class Parser18FF82A9(BaseParser):
    """
    解析 ID=0x18FF82A9
    周期: 500ms
    """

    def parse(self):
        """
        解析状态反馈和状态请求2数据
        :return: 解析后的数据字典，使用中文键名
        """
        try:
            data = [int(x, 16) for x in self.raw_data.split()]

            result = {
                "状态反馈和状态请求报文2": {
                    # Byte0-1 保留
                    "Reserve_Byte0": data[0],
                    "Reserve_Byte1": data[1],

                    # Byte2
                    "Reserve_Bit0_3": (data[2] >> 0) & 0x0F,  # Bit0-3 保留
                    "驾驶员接管提醒": self._parse_driver_takeover_req((data[2] >> 4) & 0x03),  # Bit4-5
                    "Reserve_Bit6_7": (data[2] >> 6) & 0x03,  # Bit6-7 保留

                    # Byte3-7 保留
                    "Reserve_Bytes": data[3:8] if len(data) >= 8 else []
                }
            }

            return result

        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}

    def _parse_driver_takeover_req(self, value):
        """解析驾驶员接管提醒状态"""
        states = {
            0: "未激活",
            1: "激活提醒",
            2: "预留",
            3: "预留"
        }
        return states.get(value, "未知")

