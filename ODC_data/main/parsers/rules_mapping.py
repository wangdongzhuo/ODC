from .parser_0CFE6C import Parser0CFE6C
from .parser_0CFE86A9 import Parser0CFE86A9
from .parser_18FF82A9 import Parser18FF82A9
from .parser_0CFF83AA import Parser0CFF83AA
from .parser_0CFF84A9 import Parser0CFF84A9
from .parser_0x18FF30A0 import Parser18FF30A0
from .parser_0x00000215 import Parser0x00000215
from .parser_0x00000311 import Parser0x00000311
from .parser_0x00000312 import Parser0x00000312
from .parser_0x00000321 import Parser0x00000321
from .parser_0x00000322 import Parser0x00000322
from .parser_18FA0117 import Parser18FA0117
from .parser_18FA1117 import Parser18FA1117
from .parser_18FEA297 import Parser18FEA297
from .parser_18FEBF0B import Parser18FEBF0B
from .parser_18FEE0EE import Parser18FEE0EE
from .parser_18FEF433 import Parser18FEF433
from .parser_18FF65A9 import Parser18FF65A9
from .parser_0CFF82A9 import Parser0CFF82A9
from .parser_18FF93A9 import Parser18FF93A9
from .parser_18FF7097 import Parser18FF7097
from .parser_18FFC8A0 import Parser18FFC8A0
from .parser_18FFEA97 import Parser18FFEA97
from .parser_18FFFB97 import Parser18FFFB97
from .parser_18FFF897 import Parser18FFF897
from .base_parser import BaseParser  # 默认解析器

# 映射表
RULES_MAPPING = {
    "0CFE6C17": Parser0CFE6C,
    "0CFE6CEE": Parser0CFE6C,
    "0CFF84A9": Parser0CFF84A9,
    "0CFF82A9": Parser0CFF82A9,  # 将 0CFF86A9 映射到对应解析器
    "00000215": Parser0x00000215,
    "00000312": Parser0x00000312,
    "00000311": Parser0x00000311,
    "00000321": Parser0x00000321,
    "00000322": Parser0x00000322,
    "18FA0117": Parser18FA0117,  # BC智能控制状态反馈
    "18FA1117": Parser18FA1117,  # BC智能车辆状态反馈
    "18FEBF0B": Parser18FEBF0B,  # 轮速报文
    "18FEE0EE": Parser18FEE0EE,  # BC里程信息
    "18FEF433": Parser18FEF433,  # 胎压监控系统状态
    "18FF30A0": Parser18FF30A0,  # 主目标信息
    "18FFC8A0": Parser18FFC8A0,
    "0CFE86A9": Parser0CFE86A9,  # 控制驱动和制动系统
    "0CFF83AA": Parser0CFF83AA,  # 转向系统状态反馈
    "18FEA297": Parser18FEA297,  # 域控制器基础信息1
    "18FF65A9": Parser18FF65A9,  # 协同控制系统故障
    "18FF82A9": Parser18FF82A9,  # 驾驶员接管请求
    "18FF93A9": Parser18FF93A9,  # 状态反馈和状态请求
    "18FF7097": Parser18FF7097,  # 域控制器基础信息2
    "18FFEA97": Parser18FFEA97,  # 驱动状态
    "18FFFB97": Parser18FFFB97,  # 域控制器基础信息
    "18FFF897": Parser18FFF897,  # 高压电池状态
}

def get_parser(can_id):
    """
    根据 CAN ID 返回对应的解析器类
    :param can_id: 字符串，CAN ID（如 "0CFF86A9"）
    :return: 解析器类（默认返回 BaseParser）
    """
    return RULES_MAPPING.get(can_id, BaseParser)  # 如果找不到 CAN ID，返回默认解析器
