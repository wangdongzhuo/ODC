'''
基础解析器类，定义通用解析逻辑
'''

class BaseParser:
    """
    基础解析器类，定义通用解析逻辑
    """

    def __init__(self, raw_data):
        self.raw_data = raw_data

    def parse(self):
        """
        默认解析逻辑
        :return: 默认返回未知消息
        """
        return {"Message": "Unknown CAN ID"}

