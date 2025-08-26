from .base_parser import BaseParser

class Parser0x00000311(BaseParser):
    """
    针对 CAN ID "0x00000311" 的解析器（左车道线状态 1）
    严格依据截图规则：
      - 数据总长 8 字节
      - Motorola（大端）字节序
      - 信号分布：
        - 摄像头距左车道线距离：起始位 20，长度 12 位，分辨率 0.01，偏移量 -16
        - 左车道线斜率：起始位 24，长度 11 位，分辨率 0.0009，偏移量 -0.9
        - 左车道线曲率：起始位 40，长度 12 位，分辨率 0.00001，偏移量 -0.02
        - 左车道线曲率变化率：起始位 56，长度 12 位，分辨率 0.0000001，偏移量 -0.0002048
    """

    def parse(self):
        try:
            raw_bytes = [int(byte, 16) for byte in self.raw_data.split()]
            if len(raw_bytes) != 8:
                raise ValueError("数据长度错误，应为 8 字节")

            # 1. 摄像头距左车道线距离（起始位20，12位）
            # 字节0的低4位（位20-23） + 字节1的8位（位24-31） -> 共12位
            distance_raw = ((raw_bytes[0] & 0x0F) << 8) | raw_bytes[1]
            distance = distance_raw * 0.01 - 16

            # 2. 左车道线斜率（起始位24，11位）
            # 字节2的8位（位24-31） + 字节3的高3位（位32-34） -> 共11位
            heading_raw = (raw_bytes[2] << 3) | ((raw_bytes[3] & 0xE0) >> 5)
            heading = heading_raw * 0.0009 - 0.9

            # 3. 左车道线曲率（起始位40，12位）
            # 字节5的低8位（位40-47） + 字节4的高4位（位48-51） -> 共12位
            curvature_raw = (raw_bytes[5] << 4) | ((raw_bytes[4] & 0xF0) >> 4)
            curvature = curvature_raw * 0.00001 - 0.02

            # 4. 左车道线曲率变化率（起始位56，12位）
            # 字节7的低8位（位56-63） + 字节6的高4位（位64-67） -> 共12位
            rate_raw = (raw_bytes[7] << 4) | ((raw_bytes[6] & 0xF0) >> 4)
            rate = rate_raw * 0.0000001 - 0.0002048

            return {
                "左车道线状态1": {
                    "摄像头距离左车道线距离": {
                        "数值": round(distance, 3),
                        "单位": "米",
                        "范围": "-16 ~ 15.99"
                    },
                    "左车道线斜率": {
                        "数值": round(heading, 4),
                        "单位": "无单位",
                        "范围": "-0.9 ~ 0.9"
                    },
                    "左车道线曲率": {
                        "数值": round(curvature, 5),
                        "单位": "1/米",
                        "范围": "-0.02 ~ 0.02095"
                    },
                    "左车道线的曲率变化率": {
                        "数值": round(rate, 8),
                        "单位": "1/米²",
                        "范围": "-0.0002048 ~ 0.0002047"
                    }
                }
            }
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}