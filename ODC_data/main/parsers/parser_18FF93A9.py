'''
状态反馈和状态请求报文解析器
支持ID: 0x18FF93A9
'''
from .base_parser import BaseParser

class Parser18FF93A9(BaseParser):
    """
    解析 ID=0x18FF93A9 的状态反馈和状态请求报文数据
    周期: 50ms
    """
    def parse(self):
        """
        解析状态反馈和状态请求数据
        :return: 解析后的数据字典，使用中文键名
        """
        try:
            data = [int(x, 16) for x in self.raw_data.split()]
            
            result = {
                "状态反馈和状态请求报文": {
                    "雨刮清洗请求": self._parse_binary_state(data[0] & 0x02),  # Bit1
                    
                    "除霜请求": self._parse_defrosting_req((data[1] >> 0) & 0x03),  # Bit0-1
                    
                    "司机灯开启请求": self._parse_light_state((data[2] >> 0) & 0x03),  # Bit0-1
                    
                    "前门控制请求": self._parse_door_ctrl((data[2] >> 2) & 0x03),  # Bit2-3
                    
                    "近光灯开启请求": self._parse_light_state((data[2] >> 4) & 0x03),  # Bit4-5
                    
                    "左转向灯开启请求": self._parse_light_state((data[3] >> 0) & 0x03),  # Bit0-1
                    
                    "右转向灯开启请求": self._parse_light_state((data[3] >> 2) & 0x03),  # Bit2-3
                    
                    "小灯开启请求": self._parse_light_state((data[3] >> 6) & 0x03),  # Bit6-7
                    
                    "箱灯1或日光灯开启请求": self._parse_light_state((data[4] >> 2) & 0x03),  # Bit2-3
                    
                    "喇叭开启请求": self._parse_light_state((data[4] >> 4) & 0x03),  # Bit4-5
                    
                    "中门控制请求": self._parse_door_ctrl((data[5] >> 2) & 0x03),  # Bit2-3
                    
                    "箱灯2或日光灯2开启请求": self._parse_light_state((data[5] >> 6) & 0x03),  # Bit6-7
                    
                    "前雾灯开启请求": self._parse_light_state((data[6] >> 4) & 0x03),  # Bit4-5
                    
                    "后雾灯开启请求": self._parse_light_state((data[6] >> 6) & 0x03),  # Bit6-7
                    
                    "雨刮控制请求": self._parse_wiper_ctrl((data[7] >> 2) & 0x0F),  # Bit2-4
                    
                    "危险报警闪光灯开启请求": self._parse_binary_state((data[7] >> 5) & 0x01),  # Bit5
                    
                    "远光灯开启请求": self._parse_light_state((data[7] >> 6) & 0x03),  # Bit6-7
                }
            }
            
            return result
            
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}
    
    def _parse_binary_state(self, value):
        """解析二进制状态"""
        states = {
            0: "关闭",
            1: "开启"
        }
        return states.get(value, "未知")
    
    def _parse_defrosting_req(self, value):
        """解析除霜请求状态"""
        states = {
            0: "关闭",
            1: "除霜低档开启",
            2: "除霜高档开启",
            3: "无效"
        }
        return states.get(value, "未知")
    
    def _parse_light_state(self, value):
        """解析灯光状态"""
        states = {
            0: "未激活",
            1: "激活",
            2: "NULL",
            3: "预留"
        }
        return states.get(value, "未知")
    
    def _parse_door_ctrl(self, value):
        """解析门控制状态"""
        states = {
            0: "无操作",
            1: "开门",
            2: "关门",
            3: "预留"
        }
        return states.get(value, "未知")
    
    def _parse_wiper_ctrl(self, value):
        """解析雨刮控制状态"""
        states = {
            0: "无请求",
            1: "间歇",
            2: "低速",
            3: "高速"
        }
        return states.get(value, "未知")