'''
协同控制系统故障报文解析器
支持ID: 0x18FF65A9
'''
from .base_parser import BaseParser

class Parser18FF65A9(BaseParser):
    """
    解析 ID=0x18FF65A9 的协同控制系统故障报文数据
    周期: 500ms
    """
    def parse(self):
        """
        解析协同控制系统故障数据
        :return: 解析后的数据字典，使用中文键名
        """
        try:
            data = [int(x, 16) for x in self.raw_data.split()]
            
            result = {
                "协同控制系统故障报文": {
                    "厂家代号": self._get_manufacturer_code(data[0:3]),  # Byte0-2 Bit0-12
                    "部件代号": self._get_part_code(data[1:3]),  # Byte1-2 Bit13-23
                    "故障代号": (data[3] << 8 | data[4]),  # Byte3-4
                    "部件故障等级": (data[5] >> 0) & 0x0F,  # Byte5 Bit0-2
                    "故障类型": self._parse_fault_type((data[5] >> 3) & 0x07),  # Byte5 Bit3-5
                }
            }
            
            return result
            
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}
    
    def _get_manufacturer_code(self, data):
        """解析厂家代号"""
        # 提取Byte0-2中的前13位作为厂家代号
        code = ((data[0] << 16) | (data[1] << 8) | data[2]) & 0x1FFF
        if code == 0:
            return "NULL 无效值"
        return str(code)
    
    def _get_part_code(self, data):
        """解析部件代号"""
        # 提取Byte1-2中的11位作为部件代号
        code = ((data[0] << 8) | data[1]) >> 5
        if code == 0:
            return "NULL 无效值"
        return str(code)
    
    def _parse_fault_type(self, value):
        """解析故障类型"""
        states = {
            0: "NULL 无效值",
            1: "此类故障属于，有故障时显示，故障消失则不显示",
            2: "此类故障属于，系统重新上电或初始化，则故障显示消失",
            3: "此类故障属于，一旦出现则被锁定，需要后台维修后，方可消除故障显示",
            4: "预留",
            5: "预留",
            6: "预留",
            7: "预留"
        }
        return states.get(value, "未知") 