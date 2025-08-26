#zjg16
'''
BC里程信息解析器
'''
from .base_parser import BaseParser

class Parser18FEE0EE(BaseParser):
    """
    解析 ID=0x18FEE0EE 的 BC里程信息数据
    """
    def parse(self):
        """
        解析 BC里程信息
        :return: 解析后的数据字典，使用中文键名
        """
        try:
            data = [int(x, 16) for x in self.raw_data.split()]
            
            return {
                "车辆里程总报文": {
                    "里程信息": {
                        "短里程": {
                            "数值": round(self._calculate_mileage(data[0:4]), 1),
                            "单位": "km"
                        },
                        "长里程": {
                            "数值": round(self._calculate_mileage(data[4:8]), 1),
                            "单位": "km"
                        }
                    }
                }
            }
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}

    def _calculate_mileage(self, bytes_data):
        """
        计算里程值
        :param bytes_data: 4字节里程数据
        :return: 里程值（公里）
        """
        try:
            # 将4个字节组合成32位整数
            value = (bytes_data[0] | 
                    (bytes_data[1] << 8) | 
                    (bytes_data[2] << 16) | 
                    (bytes_data[3] << 24))
            
            # 按照0.125公里/bit计算
            mileage = value * 0.125
            
            # 确保里程在有效范围内 (0-526385151.9)
            if 0 <= mileage <= 526385151.9:
                return mileage
            return 0
        except Exception:
            return 0 