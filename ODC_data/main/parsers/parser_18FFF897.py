from .base_parser import BaseParser

class Parser18FFF897(BaseParser):
    """
    解析 ID=0x18FFF897 的高压电池状态报文数据
    周期: 500ms
    """
    def parse(self):
        """
        解析高压电池状态数据
        :return: 解析后的数据字典，使用中文键名
        """
        try:
            data = [int(x, 16) for x in self.raw_data.split()]

            result = {
                "高压电池状态报文": {
                    "总电压": self._parse_battery_voltage(data[0:2]),  # Byte0-1
                    "总电流": self._parse_battery_current(data[2:4]),  # Byte2-3
                    "高压电池电量": self._parse_battery_soc(data[4]),  # Byte4
                }
            }

            return result

        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}

    def _parse_battery_voltage(self, data):
        """解析总电压
        分辨率: 0.1V/bit
        偏移量: 0
        范围: 0-1000V
        16bit
        """
        # 小端序转换：低位在前，高位在后
        voltage = ((data[1] << 8) | data[0]) * 0.1
        return f"{voltage:.1f}V"

    def _parse_battery_current(self, data):
        """解析总电流
        分辨率: 0.1A/bit
        偏移量: -600A
        范围: -600 ~ 600A
        16bit
        """
        # 小端序转换：低位在前，高位在后
        raw_current = ((data[1] << 8) | data[0])
        current = (raw_current * 0.1) - 600.0
        return f"{current:.1f}A"

    def _parse_battery_soc(self, value):
        """解析高压电池电量
        分辨率: 0.4%/bit
        8bit
        """
        soc = value * 0.4
        if 0 <= soc <= 100:
            return f"{soc:.1f}%"
        else:
            return "无效值"