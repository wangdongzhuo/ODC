import requests
import json
import time
# from api_service_HDmap import RoadInfoParser
from datetime import datetime
import threading
import os
import xml.etree.ElementTree as ET
from pyproj import Transformer

class RoadInfoParser:
    """道路信息解析器"""

    def __init__(self):
        # 定义道路类型常量
        self.URBAN_ROADS = ('快速路', '主干路', '次干路')
        self.HIGHWAY_ROADS = ('高速公路', '一级公路')
        self.RURAL_ROADS = ('正常', '乡村道路', '支路')
        self.VALID_CONDITIONS = ('正常', '异常')
        self.MAX_SLOPE = 4.0
        self.ROAD_STANDARD = "GB 14887"

    def parse_road_info(self, road_type=None, condition=None, slope=None,
                        sign_type=None, standard=None):
        """
        整合道路信息解析
        :param road_type: 道路类型
        :param condition: 道路状况
        :param slope: 坡度值
        :param sign_type: 交通设施类型
        :param standard: 道路标准
        :return: 完整的道路信息字典
        """
        result = {
            "道路基本信息": {},
            "道路状况": {},
            "坡度信息": {},
            "交通设施": {}
        }

        # 解析道路类型
        if road_type is not None:
            result["道路基本信息"] = self.parse_road_type(road_type)

        # 解析道路状况
        if condition is not None:
            result["道路状况"] = self._parse_road_condition(condition)

        # 解析坡度
        if slope is not None:
            result["坡度信息"] = self.parse_slope_degree(slope)

        # 解析交通设施
        if sign_type is not None:
            result["交通设施"] = self._parse_traffic_facility(sign_type,
                                                          standard or self.ROAD_STANDARD)

        return result

    def parse_road_type(self, road_type):
        """
        解析道路类型
        :param road_type: 道路类型字符串
        :return: 解析后的道路类型信息
        """
        # 检查输入值是否为空
        if road_type is None or road_type.strip() == '':
            return {
                "类型": "未知",
                "是否有效": False,
                "分类": "未定义",
                "描述": "道路类型数据缺失"
            }

        result = {
            "类型": road_type,
            "是否有效": False,
            "分类": None,
            "描述": None
        }

        if road_type in self.URBAN_ROADS:
            result.update({
                "是否有效": True,
                "分类": "城市道路",
                "描述": f"城市{road_type}"
            })
        elif road_type in self.HIGHWAY_ROADS:
            result.update({
                "是否有效": True,
                "分类": "高速公路",
                "描述": f"高速公路类型：{road_type}"
            })
        elif road_type in self.RURAL_ROADS:
            result.update({
                "是否有效": True,
                "分类": "乡村道路",
                "描述": f"乡村道路类型：{road_type}"
            })
        else:
            result.update({
                "描述": f"未知道路类型：{road_type}"
            })

        return result

    def _parse_road_condition(self, condition):
        """解析道路状况"""
        return {
            "状况": condition,
            "是否有效": condition in self.VALID_CONDITIONS,
            "描述": condition if condition in self.VALID_CONDITIONS else "未知状况"
        }

    def parse_slope_degree(self, slope):
        """
        解析纵断面坡度
        :param slope: 坡度值
        :return: 解析后的坡度信息
        """
        # 检查输入值是否为空
        if slope is None or str(slope).strip() == '':
            return {
                "坡度值": None,
                "是否有效": False,
                "状态": "坡度数据缺失",
                "描述": "未提供坡度数据"
            }

        try:
            slope_value = float(slope)
            result = {
                "坡度值": slope_value,
                "是否有效": slope_value <= self.MAX_SLOPE,
                "状态": "正常坡度" if slope_value <= self.MAX_SLOPE else "异常坡度",
                "描述": None
            }

            if slope_value <= self.MAX_SLOPE:
                result["描述"] = f"坡度值 {slope_value}% 在正常范围内"
            else:
                result["描述"] = f"坡度值 {slope_value}% 超出正常范围(最大{self.MAX_SLOPE}%)"

            return result
        except (ValueError, TypeError):
            return {
                "坡度值": None,
                "是否有效": False,
                "状态": "无效坡度值",
                "描述": f"无法解析的坡度值：{slope}"
            }

    def _parse_traffic_facility(self, facility_type, standard):
        """解析交通设施"""
        valid_types = {"交通标志", "交通信号灯"}

        result = {
            "类型": facility_type,
            "标准": standard,
            "是否有效": facility_type in valid_types,
            "状态": None,
            "描述": None
        }

        if facility_type in valid_types:
            result.update({
                "状态": "正常",
                "描述": f"{facility_type}符合{standard}标准"
            })
        else:
            result.update({
                "状态": "无效",
                "描述": "未知的交通设施类型"
            })

        return result

def get_root_path():
    """
    获取ODCSOFT_KINGLONG的根路径
    """
    current_path = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件的绝对路径
    root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))  # 向上回溯一层到根目录
    return root_path

def format_map_summary(data):
    """格式化地图摘要信息"""
    summary = {
        "生成时间": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "地图基础信息": {},
        "道路统计": {
            "道路总数": 0,
            "道路列表": []
        }
    }

    if "地图信息" in data:
        map_info = data["地图信息"]
        if "基础信息" in map_info:
            summary["地图基础信息"] = map_info["基础信息"]

        if "道路信息" in map_info:
            roads = map_info["道路信息"]
            summary["道路统计"]["道路总数"] = len(roads)

            for road in roads:
                road_info = {
                    "道路ID": road.get("道路ID", "未知"),
                    "道路名称": road.get("道路名称", "未知"),
                    "道路长度": road.get("道路长度", "未知"),
                    "道路几何信息": {
                        "地理坐标": road.get("地理坐标", {}),
                        "局部坐标": {
                            "x": "0",
                            "y": "0"
                        },
                        "朝向角": "0",
                        "起始位置": "0",
                        "长度": road.get("道路长度", "0")
                    },
                    "道路几何特征": {
                        "纵断面坡度": road.get("道路几何", {}).get("纵断面坡度", "-1"),
                        "道路曲率": road.get("道路几何", {}).get("道路曲率", "-1"),
                        "道路曲率半径": road.get("道路几何", {}).get("道路曲率半径", "-1")
                    },
                    "道路类型": road.get("道路类型", {}),
                    "车道特征": road.get("车道特征", {}),
                    "道路设施": road.get("道路设施", {}),
                    "限速": road.get("限速", "")
                }
                summary["道路统计"]["道路列表"].append(road_info)

    return summary

def call_map_api():
    """调用高精地图 API 并格式化输出结果"""
    url = "http://127.0.0.1:5002/get_map_data"
    root_path = get_root_path()
    filename = os.path.join(root_path, "monitorODC\\ODC_data\\main\\map_data.json")
    print(filename)
    try:
        print("[信息] 正在请求高精地图数据...")
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            
            # 格式化数据
            formatted_data = {
                "地图信息": {
                    "基础信息": data["地图信息"]["基础信息"],
                    "道路信息": []
                }
            }
            
            # 处理每条道路的信息
            if "地图信息" in data and "道路信息" in data["地图信息"]:
                for road in data["地图信息"]["道路信息"]:
                    # 获取道路几何特征
                    road_geometry = road.get("道路几何", {})
                    slope = road_geometry.get("纵断面坡度", "-1")
                    curvature = road_geometry.get("道路曲率", "-1")
                    radius = road_geometry.get("道路曲率半径", "-1")

                    road_data = {
                        "道路ID": road.get("道路ID", ""),
                        "道路名称": road.get("道路名称", ""),
                        "道路长度": road.get("道路长度", ""),
                        "道路几何信息": {
                            "地理坐标": road.get("地理坐标", {}),
                            "局部坐标": {
                                "x": road.get("地理坐标", {}).get("局部坐标", {}).get("x", "0"),
                                "y": road.get("地理坐标", {}).get("局部坐标", {}).get("y", "0")
                            },
                            "朝向角": road.get("道路几何", {}).get("朝向角", "0"),
                            "起始位置": "0",
                            "长度": road.get("道路长度", "0")
                        },
                        "道路类型": road.get("道路类型", {}),
                        "车道特征": road.get("车道特征", {}),
                        "道路设施": road.get("道路设施", {}),
                        "限速": road.get("限速", "")
                    }
                    formatted_data["地图信息"]["道路信息"].append(road_data)

            # 保存格式化后的数据到文件
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(formatted_data, f, ensure_ascii=False, indent=2)
            print(f"\n[信息] 数据已保存到 {filename}")
            
             # 打印关键信息
            for road in formatted_data["地图信息"]["道路信息"]:
                print(f"\n处理道路 ID: {road.get('道路ID', '未知')}")
                if "道路几何信息" in road:
                    geo_info = road["道路几何信息"]
                    if "地理坐标" in geo_info:
                        print(f"地理坐标:")
                        print(f"  经度: {geo_info['地理坐标'].get('经度', '未知')}")
                        print(f"  纬度: {geo_info['地理坐标'].get('纬度', '未知')}")
                
                # 打印坡度和曲率信息
                if "道路几何" in road:
                    geo_features = road["道路几何"]
                    slope = geo_features.get("纵断面坡度", "-1")
                    curvature = geo_features.get("道路曲率", "-1")
                    radius = geo_features.get("道路曲率半径", "-1")
                    
                    if slope != "-1":
                        print(f"  纵断面坡度: {slope}%")
                    if curvature != "-1":
                        print(f"  道路曲率: {curvature}")
                    if radius != "-1":
                        print(f"  道路曲率半径: {radius}米")

            return formatted_data, filename

        elif response.status_code == 204:
            print("[信息] 暂无地图数据")
        else:
            print(f"[错误] 收到意外的状态码 {response.status_code}")

    except Exception as e:
        print(f"[错误] 调用 API 时发生异常: {e}")
    return None, None

def find_road_by_coordinates(data, target_lon, target_lat, tolerance=0.0001):
    """
    在地图数据中查找指定坐标的道路
    :param data: 地图数据
    :param target_lon: 目标经度
    :param target_lat: 目标纬度
    :param tolerance: 坐标匹配的容差
    :return: 找到的道路信息或None
    """
    if not data or "地图信息" not in data:
        return None
        
    map_info = data["地图信息"]
    if "道路信息" not in map_info:
        return None
        
    for road in map_info["道路信息"]:
        if "道路几何信息" in road and "地理坐标" in road["道路几何信息"]:
            coords = road["道路几何信息"]["地理坐标"]
            road_lon = float(coords.get("经度", 0))
            road_lat = float(coords.get("纬度", 0))
            
            # 检查坐标是否在容差范围内
            if (abs(road_lon - target_lon) <= tolerance and 
                abs(road_lat - target_lat) <= tolerance):
                return road
    return None

def print_road_info(road):
    """打印道路详细信息"""
    if not road:
        print("\n未找到匹配的道路信息")
        return

    print(f"\n{'='*50}")
    print("道路详细信息:")
    print(f"{'='*50}")
    
    # 基本信息
    print("\n【基本信息】")
    print(f"道路ID: {road.get('道路ID', '未知')}")
    print(f"道路名称: {road.get('道路名称', '未知')}")
    print(f"道路长度: {road.get('道路长度', '未知')}米")
    
    # 几何信息
    if '道路几何信息' in road:
        geo = road['道路几何信息']
        print("\n【几何信息】")
        if '地理坐标' in geo:
            coords = geo['地理坐标']
            print(f"地理坐标:")
            print(f"  经度: {coords.get('经度', '未知')}")
            print(f"  纬度: {coords.get('纬度', '未知')}")
        if '局部坐标' in geo:
            local = geo['局部坐标']
            print(f"局部坐标:")
            print(f"  x: {local.get('x', '未知')}")
            print(f"  y: {local.get('y', '未知')}")
        print(f"朝向角: {geo.get('朝向角', '未知')}")
        print(f"起始位置: {geo.get('起始位置', '未知')}")
        print(f"长度: {geo.get('长度', '未知')}米")
    
    # 道路几何特征
    if '道路几何' in road:
        geo_features = road['道路几何']
        print("\n【道路几何特征】")
        slope = geo_features.get('纵断面坡度', '-1')
        if slope != '-1':
            print(f"纵断面坡度: {slope}%")
        else:
            print("纵断面坡度: 未知")
            
        curvature = geo_features.get('道路曲率', '-1')
        if curvature != '-1':
            print(f"道路曲率: {curvature}")
        else:
            print("道路曲率: 未知")
            
        radius = geo_features.get('道路曲率半径', '-1')
        if radius != '-1':
            print(f"道路曲率半径: {radius}米")
        else:
            print("道路曲率半径: 未知")

    # 道路状况
    if '道路状况' in road:
        condition = road['道路状况']
        print("\n【道路状况】")
        print(f"状态: {condition.get('condition', '未知')}")
        print(f"描述: {condition.get('description', '未知')}")
        print(f"有效性: {'有效' if condition.get('is_valid', False) else '无效'}")
    
    # 车道信息
    if '车道信息' in road:
        print("\n【车道信息】")
        for section in road['车道信息']:
            print(f"\n车道段位置: {section.get('位置', '未知')}")
            
            # 处理所有类型的车道
            for lane_type in ['中心车道', '左侧车道', '右侧车道']:
                if lane_type in section and section[lane_type]:
                    print(f"\n{lane_type}:")
                    for lane in section[lane_type]:
                        print(f"  车道ID: {lane.get('车道ID', '未知')}")
                        print(f"  车道类型: {lane.get('车道类型', '未知')}")
                        
                        if '车道属性' in lane:
                            attr = lane['车道属性']
                            print(f"  车道属性:")
                            print(f"    状态: {attr.get('状态', '未知')}")
                            print(f"    类型: {', '.join(attr.get('类型', ['未知']))}")
                        
                        if '车道标线' in lane:
                            line = lane['车道标线']
                            print(f"  车道标线:")
                            print(f"    状态: {line.get('状态', '未知')}")
                            print(f"    颜色: {', '.join(line.get('颜色', ['未知']))}")
                        
                        if '宽度' in lane and lane['宽度']:
                            width = lane['宽度']
                            print(f"  宽度信息:")
                            print(f"    宽度值: {width.get('宽度值', '未知')}米")
                            print(f"    起始位置: {width.get('起始位置', '未知')}")
                            print(f"    变化率: {width.get('变化率', '未知')}")


class RoadDataProcessor:
    def __init__(self):
        self.parser = RoadInfoParser()

    def process_road_data(self, xodr_data):
        """
        处理道路数据
        :param xodr_data: OpenDRIVE数据
        :return: 处理后的结果
        """
        try:
            # 从xodr数据中提取相关信息
            road_info = {
                "road_type": xodr_data.get("road_type"),
                "condition": xodr_data.get("condition"),
                "slope": xodr_data.get("slope"),
                "sign_type": xodr_data.get("sign_type")
            }

            # 使用解析器处理数据
            result = self.parser.parse_road_info(**road_info)

            return {
                "status": "success",
                "data": result,
                "message": "数据处理成功"
            }
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "message": f"数据处理失败: {str(e)}"
            }


def calculate_slope(elevation_data):
    """
    计算道路坡度
    :param elevation_data: 高程数据字典或对象
    :return: 坡度值 (百分比)
    """
    if not elevation_data:
        return 0.0
    
    try:
        # 获取坡度值 (b参数)
        b_param = 0
        
        # 如果是字典，直接获取b值
        if isinstance(elevation_data, dict):
            b_param = float(elevation_data.get("b", 0))
        # 如果是XML元素，从属性中获取b值
        elif hasattr(elevation_data, "get"):
            b_param = float(elevation_data.get("b", 0))
        
        # 转换为百分比
        slope_percent = b_param * 100
        return round(slope_percent, 2)  # 保留两位小数
    except (ValueError, TypeError) as e:
        print(f"[警告] 计算坡度时出错: {e}")
        return 0.0

def calculate_curvature(geometry):
    """
    计算道路曲率
    :param geometry: 道路几何信息，可以是字典或XML元素
    :return: 曲率值
    """
    try:
        # 如果是字典形式的几何信息
        if isinstance(geometry, dict):
            if "planView" in geometry:
                for segment in geometry["planView"]:
                    # 检查当前段是否为弧线
                    if "arc" in segment:
                        # 获取曲率值，取绝对值
                        return abs(float(segment.get("curvature", 0)))
            # 如果直接包含曲率字段
            elif "道路曲率" in geometry:
                curvature_str = geometry["道路曲率"]
                if curvature_str != "-1":
                    return abs(float(curvature_str))
        
        # 如果是XML元素
        elif hasattr(geometry, "find"):
            plan_view = geometry.find("planView")
            if plan_view is not None:
                for geom in plan_view.findall("geometry"):
                    arc = geom.find("arc")
                    if arc is not None and "curvature" in arc.attrib:
                        return abs(float(arc.get("curvature", 0)))
        
        return 0  # 默认返回0（直线）
    except (ValueError, TypeError) as e:
        print(f"[警告] 计算曲率时出错: {e}")
        return 0

def has_traffic_sign(road_data):
    """
    检查道路是否存在交通标志
    :param road_data: 道路数据
    :return: True/False
    """
    if "objects" in road_data:
        for obj in road_data["objects"]:
            if obj.get("type") == "trafficSign":
                return True
    return False

def has_traffic_signal(road_data):
    """
    检查道路是否存在交通信号灯
    :param road_data: 道路数据
    :return: True/False
    """
    if "signals" in road_data:
        for signal in road_data["signals"]:
            if signal.get("type") == "trafficSign":
                return True
    return False

def get_road_type(road_data):
    """
    获取道路类型
    :param road_data: 道路数据字典
    :return: 包含type字段的字典
    """
    try:
        # 检查road_data中的type字段
        if isinstance(road_data, dict) and "type" in road_data:
            type_info = road_data["type"]
            if isinstance(type_info, dict) and "type" in type_info:
                road_type = type_info["type"]
                # 返回简化的道路类型格式
                return {"type": road_type}
    except Exception as e:
        print(f"[错误] 解析道路类型时发生异常: {str(e)}")
    
    # 如果无法获取有效的道路类型，返回默认值
    return {"type": None}

def parse_xodr_file(xodr_file):
    """
    解析 xodr 文件以提取道路类型信息
    :param xodr_file: xodr 文件路径
    :return: 道路类型字典
    """
    try:
        tree = ET.parse(xodr_file)
        root = tree.getroot()

        # 查找 <type> 标签
        for type_element in root.iter('type'):
            road_type = type_element.get('type')
            if road_type:
                return road_type
        return None
    except Exception as e:
        print(f"[错误] 解析 xodr 文件时发生异常: {str(e)}")
        return None

def get_road_type_from_xodr(road_type):
    """
    根据 xodr 文件中的类型映射到中文描述
    :param road_type: xodr 文件中的道路类型
    :return: 中文描述的道路类型
    """
    type_mapping = {
        "town": "城市道路",
        "townExpressway": "城市快速路",
        "rural": "乡村道路"
    }
    return type_mapping.get(road_type, "未知")

def process_lane_info(lanes_data, lane_features):
    """
    处理车道信息
    :param lanes_data: 车道数据
    :param lane_features: 车道特征字典
    """
    try:
        if not lanes_data:
            return
        
        # 初始化车道特征
        lane_features.update({
            "是否存在车道": False,
            "车道数量": 0,
            "车道宽度": [],
            "车道标线颜色": set(),
            "车道类型": set()
        })
        
        for section in lanes_data.get("laneSection", []):
            # 处理中心车道标线
            center = section.get("center", {})
            for lane in center.get("lane", []):
                road_mark = lane.get("roadMark", {})
                if "color" in road_mark:
                    lane_features["车道标线颜色"].add(road_mark["color"])
            
            # 处理右侧车道
            right = section.get("right", {})
            for lane in right.get("lane", []):
                lane_type = lane.get("type")
                if lane_type:
                    lane_features["是否存在车道"] = True
                    lane_features["车道类型"].add(lane_type)
                
                # 获取车道宽度
                width = lane.get("width", {})
                if "a" in width:
                    lane_features["车道宽度"].append(float(width["a"]))
                
                # 获取车道标线颜色
                road_mark = lane.get("roadMark", {})
                if "color" in road_mark:
                    lane_features["车道标线颜色"].add(road_mark["color"])
        
        # 转换集合为列表，便于JSON序列化
        lane_features["车道标线颜色"] = list(lane_features["车道标线颜色"])
        lane_features["车道类型"] = list(lane_features["车道类型"])
        
        # 添加车道数量
        lane_features["车道数量"] = len(lane_features["车道宽度"])
                            
    except Exception as e:
        print(f"[错误] 处理车道信息时发生异常: {str(e)}")

def query_road_info(longitude, latitude, json_file):
    """
    查询指定坐标的道路信息
    :param longitude: 经度
    :param latitude: 纬度
    :param json_file: 地图数据JSON文件路径
    :return: 道路信息字典
    """
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            map_data = json.load(f)
        
        if "地图信息" not in map_data or "道路信息" not in map_data["地图信息"]:
            return None
            
        nearest_road = None
        min_distance = float('inf')
        
        for road in map_data["地图信息"]["道路信息"]:
            if "地理坐标" not in road:
                continue
                
            coords = road["地理坐标"]
            road_lon = float(coords.get("经度", 0))
            road_lat = float(coords.get("纬度", 0))
            
            # 计算距离
            distance = ((longitude - road_lon) ** 2 + 
                       (latitude - road_lat) ** 2) ** 0.5
            
            # 更新最近的道路
            if distance < min_distance:
                min_distance = distance
                nearest_road = road
        
        if nearest_road and min_distance <= 0.001:  # 约100米的阈值
            # 转换道路类型
            road_type = nearest_road.get("道路类型", {}).get("type", "未知")
            road_type_mapping = {
                "town": "城市道路",
                "townExpressway": "高速公路",
                "rural": "乡村道路"
            }
            converted_type = road_type_mapping.get(road_type, road_type)
            
            return {
                "道路属性": {
                    "道路类型": {"type": converted_type},
                    "道路表面": nearest_road.get("道路表面", ""),
                    "道路几何": nearest_road.get("道路几何", {})
                },
                "车道特征": nearest_road.get("车道特征", {}),
                "道路设施": nearest_road.get("道路设施", {}),
                "限速": nearest_road.get("限速", "")
            }
                
        return None
        
    except Exception as e:
        print(f"[错误] 查询过程中发生异常: {str(e)}")
        return None

class MapDataMonitor:
    def __init__(self, interval=1.0):
        self.interval = interval
        self.running = False
        self.monitor_thread = None
        self.root_path = get_root_path()
        self.xodr_file = os.path.join(self.root_path, "monitorODC\\ODC_data\\main\\chongqing0527.xodr")
        self.last_modified_time = None
        
    def initialize_data(self):
        """初始化地图数据"""
        try:
            print("[信息] 正在获取初始地图数据...")
            if not os.path.exists(self.xodr_file):
                print(f"[错误] 找不到地图文件: {self.xodr_file}")
                return False
                
            # 记录初始文件修改时间
            self.last_modified_time = os.path.getmtime(self.xodr_file)
            
            # 获取初始解析数据
            response = requests.get("http://127.0.0.1:5002/get_map_data")
            if response.status_code == 200:
                initial_data = response.json()
                # 保存初始解析数据
                with open(os.path.join(self.root_path, "monitorODC\\ODC_data\\main\\map_data.json"), 'w', encoding='utf-8') as f:
                    json.dump(initial_data, f, ensure_ascii=False, indent=2)
                print("[信息] 初始地图数据已解析并保存")
                return True
            else:
                print(f"[错误] 获取初始数据失败: 状态码 {response.status_code}")
                return False
        except Exception as e:
            print(f"[错误] 初始化数据时发生异常: {str(e)}")
            return False
    
    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            try:
                # 检查xodr文件是否存在
                if not os.path.exists(self.xodr_file):
                    print(f"[错误] 找不到地图文件: {self.xodr_file}")
                    time.sleep(self.interval)
                    continue
                
                # 获取当前文件修改时间
                current_modified_time = os.path.getmtime(self.xodr_file)
                
                # 检查文件是否被修改
                if current_modified_time != self.last_modified_time:
                    print(f"[信息] 检测到地图文件变化，正在更新解析数据...")
                    
                    # 更新文件修改时间
                    self.last_modified_time = current_modified_time
                    
                    # 获取新的解析数据
                    response = requests.get("http://127.0.0.1:5002/get_map_data")
                    if response.status_code == 200:
                        new_data = response.json()
                        
                        # 保存新的解析数据
                        with open("map_data.json", 'w', encoding='utf-8') as f:
                            json.dump(new_data, f, ensure_ascii=False, indent=2)
                        print(f"[信息] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 地图数据已更新")
                    else:
                        print(f"[错误] 获取更新数据失败: 状态码 {response.status_code}")
                
            except requests.exceptions.ConnectionError:
                print("[警告] 无法连接到服务器，将在下次循环重试")
            except Exception as e:
                print(f"[错误] 监控过程中发生异常: {e}")
            
            time.sleep(self.interval)
    
    def start_monitoring(self):
        """启动监控线程"""
        # 首先初始化数据
        if not os.path.exists("map_data.json"):
            if not self.initialize_data():
                print("[错误] 无法初始化地图数据，监控启动失败")
                return False
        
        if not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            print("[信息] 地图文件监控已启动")
            return True
        return False
    
    def stop_monitoring(self):
        """停止监控线程"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
            print("[信息] 地图文件监控已停止")

class CoordinateConverter:
    def __init__(self):
        try:
            # 更新坐标系统参数
            self.proj_params = (
                "+proj=tmerc "        # 横轴墨卡托投影
                "+lat_0=0 "           # 起始纬度
                "+lon_0=105 "         # 中央经线
                "+k=1 "               # 比例因子
                "+x_0=-129900 "       # X方向偏移
                "+y_0=-3267000 "      # Y方向偏移
                "+zone=50 "           # 投影带号
                "+ellps=WGS84 "       # 参考椭球
                "+units=m "           # 单位：米
                "+no_defs"            # 不使用预定义参数
            )
            
            # 创建坐标转换器
            self.transformer = Transformer.from_crs(
                self.proj_params,
                "EPSG:4326",  # WGS84经纬度
                always_xy=True
            )
            print("[信息] 坐标转换器初始化成功")
        except Exception as e:
            print(f"[错误] 坐标转换器初始化失败: {e}")
            raise

def main():
    """主函数"""
    print("\n[提示] 请确保 api_service_高精地图.py 已经启动")
    time.sleep(2)
    
    # 创建并启动监控器
    monitor = MapDataMonitor()
    if not monitor.start_monitoring():
        print("[错误] 监控启动失败，程序退出")
        return
    
    try:
        print("\n[信息] 地图文件监控已启动，按Ctrl+C退出...")
        while True:
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n[信息] 收到退出信号")
    finally:
        monitor.stop_monitoring()
        print("\n程序结束")


if __name__ == "__main__":
    main()
