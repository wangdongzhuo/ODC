import time
import os
import xml.etree.ElementTree as ET
from api_service_HDmap import RoadInfoParser

def get_root_path():
    """
    获取ODCSOFT_KINGLONG的根路径
    """
    current_path = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件的绝对路径
    root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))  # 向上回溯三层到根目录
    return root_path

# 使用相对路径构建完整路径
root_path = get_root_path()
source_file = os.path.join(root_path, "monitorODC\\ODC_data\\data-original\\chongqing0527.xodr")

# 输出文件（实时更新的目标文件）
target_file = os.path.join(root_path, "monitorODC\\ODC_data\\data-real-time\\chongqing0527.xodr")

class MapDataSimulator:
    """高精地图数据模拟器"""
    
    def __init__(self, source_file, target_file):
        self.source_file = source_file
        self.target_file = target_file
        self.tree = None
        self.root = None
        self.road_parser = RoadInfoParser()
        
    def ensure_target_file_exists(self):
        """检查目标文件是否存在，如果不存在则创建"""
        target_dir = os.path.dirname(self.target_file)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            print(f"[信息] 创建目录: {target_dir}")
            
        if not os.path.exists(self.target_file):
            with open(self.target_file, "w", encoding='utf-8') as file:
                file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                file.write('<!-- 实时模拟的高精地图数据 -->\n')
                file.write('<OpenDRIVE>\n</OpenDRIVE>')
            print(f"[信息] 创建新文件: {self.target_file}")
    
    def load_source_file(self):
        """加载源文件"""
        try:
            self.tree = ET.parse(self.source_file)
            self.root = self.tree.getroot()
            print("[信息] 成功加载源文件")
            return True
        except Exception as e:
            print(f"[错误] 加载源文件失败: {e}")
            return False
            
    def process_road_element(self, element):
        """
        处理道路元素
        :param element: XML道路元素
        :return: 处理后的道路信息
        """
        try:
            # 提取道路信息
            road_data = {
                "road_type": element.get("type"),
                "condition": element.find("surface").get("condition") if element.find("surface") is not None else None,
                "slope": element.find("elevation").get("slope") if element.find("elevation") is not None else None,
                "sign_type": element.find("signal").get("type") if element.find("signal") is not None else None
            }
            # 使用解析器处理数据
            return self.road_parser.parse_road_info(**road_data)
        except Exception as e:
            print(f"[警告] 处理道路元素时出错: {str(e)}")
            return None

    def simulate_real_time_data(self):
        """模拟实时写入地图数据"""
        if not self.load_source_file():
            return
            
        print("[信息] 开始模拟实时数据写入...")
        
        for road in self.root.findall("road"):
            print(road)
            print("--------------------------------")
            try:
                # 处理道路信息
                road_info = self.process_road_element(road)
                if road_info:
                    print(road_info)
                    print(f"[信息] 处理道路ID {road.get('id', 'unknown')}: {road_info}")
                
                # 模拟处理时间
                time.sleep(0.5)
                
            except Exception as e:
                print(f"[错误] 处理道路时出错: {str(e)}")
                continue
        
        print("[信息] 数据处理完成")
        
    def _save_target_file(self, tree):
        """保存到目标文件"""
        try:
            tree.write(self.target_file, encoding='utf-8', xml_declaration=True)
        except Exception as e:
            print(f"[错误] 保存文件失败: {e}")
            
def main():
    """主函数"""
    print("[信息] 启动高精地图数据模拟器...")
    
    # 检查源文件是否存在
    if not os.path.exists(source_file):
        print(f"[错误] 源文件不存在: {source_file}")
        return
        
    # 创建模拟器实例
    simulator = MapDataSimulator(source_file, target_file)
    
    # 确保目标文件存在
    simulator.ensure_target_file_exists()
    
    # 开始模拟数据写入
    simulator.simulate_real_time_data()

if __name__ == "__main__":
    main() 