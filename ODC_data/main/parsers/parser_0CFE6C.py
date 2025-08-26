from .base_parser import BaseParser


class Parser0CFE6C(BaseParser):
    """
    解析 ID=0x0CFE6C17 和 0x0CFE6CEE 的车辆车速报文数据
    """

    def parse(self):
        """
        解析车辆车速数据
        :return: 解析后的数据字典，使用中文键名
        分辨率: 1/256公里/小时/bit
        偏移量: 0
        范围: 0-250.996公里/小时
        """
        try:
            data = [int(x, 16) for x in self.raw_data.split()]

            # 检查数据长度是否为8字节
            if len(data) != 8:
                raise ValueError("数据长度不符合要求，应为8字节")

            # 车速值在Byte6和Byte7
            byte6 = data[6]
            byte7 = data[7]

            # 将两个字节组合成16位整数
            speed_value = (byte6 | (byte7 << 8))

            # 按照1/256公里/小时/bit计算实际速度
            speed = speed_value / 256.0

            # 确保速度在有效范围内 (0-250.996)
            if 0 <= speed <= 250.996:
                result = {
                    "车辆车速报文": {
                        "车速值": round(speed, 3)  # 保留3位小数
                    }
                }
            else:
                result = {
                    "车辆车速报文": {
                        "车速值": 0.0  # 超出范围返回0
                    }
                }

            return result
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}