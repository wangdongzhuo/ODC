'''
L2功能状态反馈报文解析器
支持ID: 0x18FFC897
'''
from .base_parser import BaseParser

class Parser18FFC8A0(BaseParser):
    """
    解析 ID=0x18FFC8A0 的L2功能状态反馈报文数据
    周期: 50ms
    """
    def parse(self):
        """
        解析L2功能状态反馈数据
        :return: 解析后的数据字典，使用中文键名
        """
        try:
            data = [int(x, 16) for x in self.raw_data.split()]
            
            result = {
                "L2功能状态反馈": {
                    "ACC工作状态": self._parse_acc_work_status((data[0] >> 0) & 0x07),  # Byte0 Bit0-2
                    "ACC工作模式": self._parse_acc_work_mode((data[0] >> 3) & 0x07),  # Byte0 Bit3-5
                    "ACC开启且未达到功能自动条件原因": self._parse_acc_not_ready((data[1] >> 0) & 0x0F),  # Byte1 Bit0-3
                    "ACC功能激活退出原因": self._parse_acc_quit_reason((data[1] >> 4) & 0x0F),  # Byte1 Bit4-7
                    "LKA工作状态": self._parse_lka_work_status((data[2] >> 0) & 0x07),  # Byte2 Bit0-2
                    "LKA功能激活退出原因": self._parse_lka_quit_reason((data[2] >> 3) & 0x1F),  # Byte2 Bit3-7
                    "LKA开启且未达到功能自动条件原因": self._parse_lka_not_ready((data[3] >> 0) & 0x1F),  # Byte3 Bit0-4
                    "LDW工作状态": self._parse_ldw_status((data[3] >> 5) & 0x07),  # Byte3 Bit5-7
                    "L2功能激活模式": self._parse_l2_active_mode((data[4] >> 0) & 0x07),  # Byte4 Bit0-2
                    "CMS&AEB系统工作状态": self._parse_cms_status((data[5] >> 0) & 0x07),  # Byte5 Bit0-2
                    "CMS&AEB警告等级": self._parse_cms_warning_level((data[5] >> 3) & 0x07),  # Byte5 Bit3-5
                }
            }
            
            return result
            
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}
    
    def _parse_acc_work_status(self, value):
        """解析ACC工作状态"""
        states = {
            0: "初始化",
            1: "关闭",
            2: "开启",
            3: "待机",
            4: "激活",
            5: "超速控制",
            6: "抑制",
            7: "故障"
        }
        return states.get(value, "未知")
    
    def _parse_acc_work_mode(self, value):
        """解析ACC工作模式"""
        states = {
            0: "无",
            1: "定速控制",
            2: "跟随控制",
            3: "停车控制",
            4: "自动控制",
            5: "无效",
            6: "无效",
            7: "无效"
        }
        return states.get(value, "未知")
    
    def _parse_acc_not_ready(self, value):
        """解析ACC开启且未达到功能自动条件原因"""
        states = {
            0: "无不满足条件",
            1: "档位不满足",
            2: "手刹未松开",
            3: "脚车未松开",
            4: "油门开度大于60%",
            5: "车辆模式不满足",
            6: "ACC系统自检错误",
            7: "按键（优先）操作关闭",
            8: "前刹车中中高速档位",
            9: "车道宽度不满足",
            10: "车道数量信息不满足",
            11: "道路曲率半径不满足"
        }
        return states.get(value, "未知")
    
    def _parse_acc_quit_reason(self, value):
        """解析ACC功能激活退出原因"""
        states = {
            0: "无不满足条件",
            1: "ACC目标未跟上",
            2: "车辆手刹激活拉起",
            3: "车辆模式不满足",
            4: "车辆位置未处于前进档",
            5: "ACC_Cancel",
            6: "前刹开启中高档位",
            7: "车道宽不满足",
            8: "车道数量信息不满足",
            9: "道路曲率半径不满足",
            10: "油门开度大于阈值且持续一定时间",
            11: "可机器操动",
            12: "实际车速小于ACC允许最低车速",
            13: "协同控制触发关闭"
        }
        return states.get(value, "未知")
    
    def _parse_lka_work_status(self, value):
        """解析LKA工作状态"""
        states = {
            0: "无效",
            1: "关闭",
            2: "待机",
            3: "激活",
            4: "退出",
            5: "故障",
            6: "无效",
            7: "无效"
        }
        return states.get(value, "未知")
    
    def _parse_lka_quit_reason(self, value):
        """解析LKA功能激活退出原因"""
        states = {
            0: "无不满足条件",
            1: "车辆模式不满足",
            2: "方向盘当前实际扭矩大于一定阈值",
            3: "前向防撞CMS功能激活",
            4: "ACC功能退出",
            5: "转向灯开启",
            6: "驾驶员油门门槛出",
            7: "深踩制动",
            8: "驾驶员操控持续时间超过一定阈值",
            9: "前刹开启中高档位",
            10: "无道路无效",
            11: "车道线数量信息不满足",
            12: "道路曲率半径不满足",
            13: "车速超过最高限速",
            14: "按键（优先）操作关闭",
            15: "协同控制触发关闭",
            16: "静同控制触发关闭"
        }
        return states.get(value, "未知")
    
    def _parse_lka_not_ready(self, value):
        """解析LKA开启且未达到功能自动条件原因"""
        states = {
            0: "无不满足条件",
            1: "车辆档位不满足",
            2: "方向盘当前实际扭矩不满足",
            3: "无道路",
            4: "方向盘转向实际角度不满足",
            5: "ACC未激活",
            6: "转向灯开启",
            7: "油门踏板不满足",
            8: "制动踏板不满足",
            9: "可机离开",
            10: "前刹开启中高速档位",
            11: "车道宽度不满足",
            12: "车道数量信息不满足",
            13: "道路曲率半径不满足",
            14: "车速不满足",
            15: "横风加速度不满足",
            16: "手刹未释放",
            17: "车辆模式不满足（存在故障）"
        }
        return states.get(value, "未知")
    
    def _parse_ldw_status(self, value):
        """解析LDW工作状态"""
        states = {
            0: "无效",
            1: "关闭",
            2: "待机",
            3: "激活",
            4: "故障",
            5: "无效",
            6: "无效",
            7: "无效"
        }
        return states.get(value, "未知")
    
    def _parse_l2_active_mode(self, value):
        """解析L2功能激活模式"""
        states = {
            0: "未激活",
            1: "LKA同向协助功能激活",
            2: "ACC同向协助功能激活",
            3: "L2功能激活（横纵向同步开启ACC&LKA）",
            4: "CMS&AEB功能激活",
            5: "预留",
            6: "预留",
            7: "预留"
        }
        return states.get(value, "未知")
    
    def _parse_cms_status(self, value):
        """解析CMS&AEB系统工作状态"""
        states = {
            0: "初始化",
            1: "关闭",
            2: "开启",
            3: "激活",
            4: "故障",
            5: "预留",
            6: "预留",
            7: "预留"
        }
        return states.get(value, "未知")
    
    def _parse_cms_warning_level(self, value):
        """解析CMS&AEB警告等级"""
        states = {
            0: "无生效",
            1: "车距预警（车辆一级碰撞预警）",
            2: "车距预警（CMS&AEB紧急制动预警）",
            3: "行人一级碰撞预警",
            4: "行人二级碰撞预警",
            5: "行人CMS&AEB紧急制动激活",
            6: "无效",
            7: "无效"
        }
        return states.get(value, "未知") 