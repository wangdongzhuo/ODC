#mjz
from .base_parser import BaseParser

class Parser18FF30A0(BaseParser):
    """
    针对 CAN ID "18FF30A0" 的解析器
    """

    def parse(self):
        """
        解析数据
        :return: 解析后的字典，使用中文键名
        """
        try:
            raw_bytes = [int(byte, 16) for byte in self.raw_data.split()]

            # Byte0: 主目标标志类型
            obstacle_type_bits = raw_bytes[0] & 0x07
            obstacle_type_mapping = {
                0: "无效（无主目标）",
                1: "行人",
                2: "骑车人",
                3: "汽车",
                4: "未知",
                5: "未工作",
            }
            obstacle_type = obstacle_type_mapping.get(obstacle_type_bits, "预留")

            # Byte1 ~ Byte2: 主目标相对位置X
            raw_val_x = raw_bytes[1] | (raw_bytes[2] << 8)
            if raw_val_x == 0xFFFF:
                position_x = 4095.9375  # 当无主目标时
            else:
                position_x = raw_val_x * 0.0625

            # Byte3: 主目标相对位置Y
            position_y = (raw_bytes[3] * 0.0625) - 32

            # Byte4: 与主目标相对速度X
            rel_velocity_x = (raw_bytes[4] * 0.0625) - 31.93

            # Byte5: 与主目标相对速度Y
            rel_velocity_y = (raw_bytes[5] * 0.0625) - 31.93

            # Byte6: 标志位
            connect_fault = (raw_bytes[6] >> 4) & 0x01
            fusion_fault = (raw_bytes[6] >> 5) & 0x01

            connect_fault_status = "无故障" if connect_fault == 0 else "有故障"
            fusion_fault_status = "无故障" if fusion_fault == 0 else "有故障"

            # 返回解析结果
            return {
                "主目标信息": {
                    "主目标标志类型": {
                        "数值": obstacle_type_bits,
                        "状态": obstacle_type
                    },
                    "主目标相对位置X": {
                        "数值": round(position_x, 3),
                        "单位": "米",
                        "状态说明": "范围：0~4095.9375"
                    },
                    "主目标相对位置Y": {
                        "数值": round(position_y, 3),
                        "单位": "米",
                        "状态说明": "范围：-32 ~ 31.9375"
                    },
                    "与主目标相对速度X": {
                        "数值": round(rel_velocity_x, 3),
                        "单位": "米/秒",
                        "状态说明": "范围：-31.93 ~ 31.93"
                    },
                    "与主目标相对速度Y": {
                        "数值": round(rel_velocity_y, 3),
                        "单位": "米/秒",
                        "状态说明": "范围：-31.93 ~ 31.93"
                    },
                    "车辆连接故障": {
                        "数值": connect_fault,
                        "状态": connect_fault_status
                    },
                    "感知融合故障": {
                        "数值": fusion_fault,
                        "状态": fusion_fault_status
                    }
                }
            }
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}
