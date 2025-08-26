#mjz
from .base_parser import BaseParser

class Parser0CFF84A9(BaseParser):
    """
    针对 CAN ID "0CFF84A9" 的解析器
    """

    def parse(self):
        """
        解析数据
        :return: 解析后的字典，使用中文键名
        """
        try:
            raw_bytes = [int(byte, 16) for byte in self.raw_data.split()]

            # Byte0 ~ Byte1: 方向盘角度指令
            angle_request = (raw_bytes[0] | (raw_bytes[1] << 8)) * 0.1 - 3000

            # Byte2: 工作模式和使能信号
            work_mode = bin(raw_bytes[2] & 0x0F)[2:].zfill(4)
            enable_signal = bin((raw_bytes[2] >> 4) & 0x03)[2:].zfill(2)

            # Byte3: 转矩叠加
            steering_torque = (raw_bytes[3] - 128) * 0.12

            # Byte4: 方向盘目标转速
            steering_speed = raw_bytes[4] * 0.1

            # Byte7: 生命周期信号
            life_signal = bin(raw_bytes[7] & 0x0F)[2:].zfill(4)

            # 工作模式映射
            work_mode_mapping = {
                "0000": "预留",
                "0001": "自动驾驶模式指令",
                "0010": "预留",
                "0011": "力矩叠加模式指令",
                "0100": "手动方向盘恢复",
                "0101": "手动介入恢复指令",
                "0110": "清除恢复指令",
                "0111": "预留"
            }

            # 使能信号映射
            enable_signal_mapping = {
                "00": "未激活",
                "01": "无效",
                "10": "无效",
                "11": "激活"
            }

            return {
                "控制转向系统报文": {
                    "方向盘角度指令": {
                        "数值": round(angle_request, 1),
                        "单位": "度",
                        "状态说明": "范围：-3000 ~ 3000"
                    },
                    "工作模式": {
                        "数值": work_mode,
                        "状态": work_mode_mapping.get(work_mode, "未知模式")
                    },
                    "转向控制使能": {
                        "数值": enable_signal,
                        "状态": enable_signal_mapping.get(enable_signal, "未知状态")
                    },
                    "转向叠加扭矩": {
                        "数值": round(steering_torque, 2),
                        "单位": "Nm",
                        "状态说明": "范围：-12.8 ~ 12.7"
                    },
                    "方向盘目标角速度": {
                        "数值": round(steering_speed, 1),
                        "单位": "度/秒",
                        "状态说明": "范围：100 ~ 540"
                    },
                    "生命周期信号": {
                        "数值": int(life_signal, 2),
                        "状态说明": "范围：0 ~ 15"
                    }
                }
            }
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}
