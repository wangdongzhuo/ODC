from .base_parser import BaseParser

class Parser0x00000312(BaseParser):
    """
    针对 CAN ID "0x00000312" 的解析器（左车道线状态 2）
    根据截图信息解析 Lane1_Confidence（左车道线置信度）：
      - 起始位：9
      - 长度：3 位
      - 排列模式：Motorola（大端）
      - 分辨率：1
      - 偏移量：0
      - 数值范围：0~7
    """

    def parse(self):
        """
        解析数据
        :return: 解析后的字典，使用中文键名
        """
        try:
            # 将十六进制字符串转换为字节列表
            raw_bytes = [int(byte, 16) for byte in self.raw_data.split()]

            # 确认数据长度为 8 字节
            if len(raw_bytes) != 8:
                raise ValueError("数据长度错误，应为 8 字节")

            # 在 Motorola 大端格式下，start_bit=9, length=3 对应 Byte1 的 bits[6..4]
            # 提取方式：右移 4 位后，再与 0x07 (三位掩码) 相与
            lane_confidence = (raw_bytes[1] >> 4) & 0x07

            return {
                "左车道线状态2": {
                    "左车道线置信度": {
                        "数值": lane_confidence,
                        "状态说明": "范围：0 ~ 7，值越大置信度越高"
                    }
                }
            }
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}