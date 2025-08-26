'''
转向系统状态反馈报文解析器
支持ID: 0x0CFF83AA
'''
from .base_parser import BaseParser

class Parser0CFF83AA(BaseParser):
    """
    解析 ID=0x0CFF83AA 的转向系统状态反馈报文数据
    周期: 20ms
    """
    def parse(self):
        """
        解析转向系统状态反馈数据
        :return: 解析后的数据字典，使用中文键名
        """
        try:
            data = [int(x, 16) for x in self.raw_data.split()]
            
            result = {
                "转向系统状态反馈": {
                    "方向盘当前实际扭矩": self._parse_strg_torq(data[1]),  # Byte1
                    "电机助力扭矩低字节": self._parse_motor_torq_low(data[2]),  # Byte2
                    "电机助力扭矩高字节": self._parse_motor_torq_high(data[3]),  # Byte3
                    "目标方向盘转向实际角度低字节": self._parse_angle_real_low(data[4]),  # Byte4
                    "目标方向盘转向实际角度高字节": self._parse_angle_real_high(data[5]),  # Byte5
                    "方向盘当前实际转速": self._parse_angle_speed(data[6]),  # Byte6
                    "当前系统实际工作状态": self._parse_work_mode((data[7] >> 0) & 0x0F),  # Byte7 Bit0-3
                    "life生命信号": (data[7] >> 4) & 0x0F  # Byte7 Bit4-7
                }
            }
            
            return result
            
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}
    
    def _parse_strg_torq(self, value):
        """解析方向盘当前实际扭矩
        分辨率: 0.1Nm/位
        偏移量: -12.8
        范围: 0-255, 对应-12.8Nm ~ 12.8Nm
        """
        if value == 0x80:
            return "0Nm"
        torque = (value * 0.1) - 12.8
        return f"{torque:.1f}Nm"
    
    def _parse_motor_torq_low(self, value):
        """解析电机助力扭矩低字节
        分辨率: 0.001Nm/位
        偏移量: -30
        范围: 0-60000, 对应-30Nm ~ 30Nm
        """
        return value
    
    def _parse_motor_torq_high(self, value):
        """解析电机助力扭矩高字节"""
        if value == 0x7530:
            return "0Nm"
        return value
    
    def _parse_angle_real_low(self, value):
        """解析目标方向盘转向实际角度低字节
        分辨率: 0.1°/位
        范围: <3000
        """
        return value
    
    def _parse_angle_real_high(self, value):
        """解析目标方向盘转向实际角度高字节
        范围: 0-60000, 对应角度 -3000 ~ 3000
        """
        if value == 0x7530:
            return "方向盘中间位"
        return value
    
    def _parse_angle_speed(self, value):
        """解析方向盘当前实际转速
        分辨率: 10°/s
        偏移量: 0
        范围: 0-255, 对应0°/s ~ 2550°/s
        """
        if value == 0x0A:
            return "100°/s"
        speed = value * 10
        return f"{speed}°/s"
    
    def _parse_work_mode(self, value):
        """解析当前系统实际工作状态"""
        states = {
            0: "自机模式",
            1: "自动驾驶模式",
            2: "预留",
            3: "力矩叠加模式",
            4: "力矩模式",
            5: "手动介入模式",
            6: "管控模式",
            7: "管控模式（故障模式）",
            8: "预留",
            9: "预留",
            10: "预留",
            11: "预留",
            12: "预留",
            13: "预留",
            14: "预留",
            15: "预留"
        }
        return states.get(value, "未知") 