'''
域控制器基础信息报文解析器
支持ID: 0x18FFFB97
'''
from .base_parser import BaseParser

class Parser18FFFB97(BaseParser):
    """
    解析 ID=0x18FFFB97 的域控制器基础信息报文数据
    周期: 500ms
    """
    def parse(self):
        """
        解析域控制器基础信息数据
        :return: 解析后的数据字典，使用中文键名
        """
        try:
            data = [int(x, 16) for x in self.raw_data.split()]
            
            result = {
                "域控制器基础信息": {
                    "剩余里程": self._parse_driving_distance(data[4:6]),  # Byte4-5
                }
            }
            
            return result
            
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}
    
    def _parse_driving_distance(self, data):
        """解析剩余里程
        分辨率: 0.1km/bit
        偏移量: 0
        """
        distance = ((data[0] << 8) | data[1]) * 0.1
        return f"{distance:.1f}km" 