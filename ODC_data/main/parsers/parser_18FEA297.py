'''
域控制器基础信息报文1解析器
支持ID: 0x18FEA297
'''
from .base_parser import BaseParser

class Parser18FEA297(BaseParser):
    """
    解析 ID=0x18FEA297 的域控制器基础信息1报文数据
    周期: 100ms
    """
    def parse(self):
        """
        解析域控制器基础信息1数据
        :return: 解析后的数据字典，使用中文键名
        """
        try:
            data = [int(x, 16) for x in self.raw_data.split()]
            
            result = {
                "域控制器基础信息1": {
                    "当前档位": self._parse_current_gear((data[0] >> 0) & 0x07),  # Byte0 Bit0-2
                    "车辆当前高压驱动状态": self._parse_veh_drive_st((data[0] >> 3) & 0x07),  # Byte0 Bit3-5
                    "当前P档位状态": self._parse_parking_st((data[0] >> 6) & 0x03),  # Byte0 Bit6-7
                    "转向助力油泵状态": self._parse_strg_pump_st((data[3] >> 0) & 0x03),  # Byte3 Bit0-2
                }
            }
            
            return result
            
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}
    
    def _parse_current_gear(self, value):
        """解析当前档位"""
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
    
    def _parse_veh_drive_st(self, value):
        """解析车辆当前高压驱动状态"""
        states = {
            0: "无效",
            1: "上电过程",
            2: "驱动模式",
            3: "滑行模式",
            4: "准备就绪",
            5: "被行准备",
            6: "预留",
            7: "预留"
        }
        return states.get(value, "未知")
    
    def _parse_parking_st(self, value):
        """解析当前P档位状态"""
        states = {
            0: "释放",
            1: "驻车",
            2: "预留",
            3: "预留"
        }
        return states.get(value, "未知")
    
    def _parse_strg_pump_st(self, value):
        """解析转向助力油泵状态"""
        states = {
            0: "熄灭",
            1: "上电",
            2: "故障",
            3: "诊断"
        }
        return states.get(value, "未知")

