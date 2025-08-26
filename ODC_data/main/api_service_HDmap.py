from flask import Flask, jsonify, request
import xml.etree.ElementTree as ET
import os
from pyproj import Transformer, CRS
import numpy as np

app = Flask(__name__)

def get_root_path():
    """
    获取ODCSOFT_KINGLONG的根路径
    """
    current_path = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件的绝对路径
    root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))  # 向上回溯三层到根目录
    return root_path

# 使用相对路径构建完整路径
root_path = get_root_path()
file_path = os.path.join(root_path, "monitorODC\\ODC_data\\main\\chongqing0527.xodr")

class CoordinateConverter:
    """坐标转换器"""
    
    def __init__(self):
        # 使用正确的投影参数
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
    
    def local_to_wgs84(self, x, y):
        """
        局部坐标转换为WGS84经纬度
        :param x: 局部坐标x
        :param y: 局部坐标y
        :return: (lon, lat) 经纬度坐标
        """
        try:
            # 进行坐标转换
            lon, lat = self.transformer.transform(x, y)
            
            # 确保经纬度在合理范围内
            if -180 <= lon <= 180 and -90 <= lat <= 90:
                return round(lon, 6), round(lat, 6)
            else:
                print(f"[警告] 转换后的坐标超出范围: lon={lon}, lat={lat}")
                return None, None
        except Exception as e:
            print(f"[错误] 坐标转换失败: {e}")
            return None, None

class OpenDriveParser:
    """OpenDRIVE 地图文件解析器"""
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.tree = None
        self.root = None
        self.coordinate_converter = CoordinateConverter()
        
    def parse(self):
        """解析 OpenDRIVE 文件"""
        try:
            if not os.path.exists(self.file_path):
                return {"错误信息": f"文件不存在: {self.file_path}"}
                
            self.tree = ET.parse(self.file_path)
            self.root = self.tree.getroot()
            return self._parse_map_data()
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}
            
    def _parse_map_data(self):
        """解析地图数据"""
        try:
            return {
                "地图信息": {
                    "基础信息": self._parse_header(),
                    "道路信息": self._parse_roads(),
                    "路口信息": self._parse_junctions()
                }
            }
        except Exception as e:
            return {"错误信息": f"解析错误: {str(e)}"}
            
    def _parse_header(self):
        """解析地图头文件信息"""
        header = self.root.find('header')
        if header is not None:
            return {
                "版本": header.get('revMajor', '') + '.' + header.get('revMinor', ''),
                "名称": header.get('name', ''),
                "日期": header.get('date', ''),
                "经度": header.get('west', ''),
                "纬度": header.get('south', ''),
                "海拔": header.get('elevation', '')
            }
        return {}
        
    def _parse_roads(self):
        """解析道路信息"""
        roads_data = []
        for road in self.root.findall('road'):
            road_data = {
                "道路ID": road.get('id', ''),
                "道路名称": road.get('name', ''),
                "道路长度": road.get('length', ''),
                "道路类型": self._parse_road_type(road),
                "车道特征": self._parse_lanes(road),
                "地理坐标": self._parse_geometry(road),
                "道路表面": self._parse_road_surface(road),
                "道路几何": self._parse_road_geometry(road),
                "道路设施": self._parse_road_facilities(road),
                "限速": self._parse_speed_limit(road)
            }
            roads_data.append(road_data)
        return roads_data
        
    def _parse_lanes(self, road):
        """解析车道信息"""
        lanes_data = {
            "标线质量": [],
            "是否存在车道": False,
            "车道宽度": [],
            "车道标线颜色": set(),
            "车道类型": set(),
            "车道数量": []
        }
        
        lane_sections = road.findall('lanes/laneSection')
        for section in lane_sections:
            for lane in section.findall('right/lane'):
                lane_type = lane.get('type')
                if lane_type:
                    lanes_data["车道类型"].add(lane_type)
                    lanes_data["是否存在车道"] = True
                
                width_elements = lane.findall('width')
                for width in width_elements:
                    width_value = width.get('a', "-1")  # 默认值设为"-1"
                    lanes_data["车道宽度"].append(float(width_value) if width_value != "-1" else "-1")
                
                road_mark = lane.find('roadMark')
                if road_mark is not None:
                    lanes_data["车道标线颜色"].add(road_mark.get('color', '未知'))
                    lanes_data["标线质量"].append(road_mark.get('width', '-1'))  # 默认值设为"-1"
                
                lanes_data["车道数量"].append(int(lane.get('id', '-1')))  # 默认值设为"-1"
        
        # 如果没有找到任何车道信息，设置默认值
        if not lanes_data["车道宽度"]:
            lanes_data["车道宽度"] = ["-1"]
        if not lanes_data["标线质量"]:
            lanes_data["标线质量"] = ["-1"]
        if not lanes_data["车道数量"]:
            lanes_data["车道数量"] = ["-1"]
        if not lanes_data["车道标线颜色"]:
            lanes_data["车道标线颜色"] = ["未知"]
        if not lanes_data["车道类型"]:
            lanes_data["车道类型"] = ["未知"]
        
        # 转换集合为列表
        lanes_data["车道标线颜色"] = list(lanes_data["车道标线颜色"])
        lanes_data["车道类型"] = list(lanes_data["车道类型"])
        
        return lanes_data

    def _parse_road_type(self, road):
        """解析道路类型"""
        road_type_element = road.find('type')
        if road_type_element is not None:
            road_type = road_type_element.get('type', '未知')
            # 转换道路类型
            road_type_mapping = {
                "town": "城市道路",
                "townExpressway": "高速公路",
                "rural": "乡村道路"
            }
            converted_type = road_type_mapping.get(road_type, road_type)
            return {"type": converted_type}
        return {"type": "未知"}

    def _parse_junctions(self):
        """解析路口信息"""
        junctions_data = []
        for junction in self.root.findall('junction'):
            junction_data = {
                "路口ID": junction.get('id', ''),
                "路口名称": junction.get('name', ''),
                "连接信息": self._parse_connections(junction)
            }
            junctions_data.append(junction_data)
        return junctions_data
        
    def _parse_connections(self, junction):
        """解析路口连接信息"""
        connections = []
        for connection in junction.findall('connection'):
            connection_data = {
                "连接ID": connection.get('id', ''),
                "入口道路": connection.get('incomingRoad', ''),
                "连接道路": connection.get('connectingRoad', ''),
                "接触点": connection.get('contactPoint', '')
            }
            connections.append(connection_data)
        return connections

    def parse_road_condition(self, condition):
        """
        解析道路表面状况
        :param condition: 道路状况字符串
        :return: 状况描述和验证结果
        """
        valid_conditions = ('正常', '异常')
        
        result = {
            "condition": condition,
            "is_valid": condition in valid_conditions,
            "description": "待定，预留接口持续输出"
        }
        
        if condition == "正常":
            result["description"] = "正常"
        elif condition == "异常":
            result["description"] = "异常"
            
        return result

    def parse_slope_degree(self, slope):
        """
        解析纵断面坡度
        :param slope: 坡度值
        :return: 坡度状态和验证结果
        """
        try:
            slope_value = float(slope)
            result = {
                "slope": slope_value,
                "is_valid": slope_value <= 4,
                "status": None
            }
            
            if slope_value <= 4:
                result["status"] = "正常坡度"
            else:
                result["status"] = "异常坡度"
                
            return result
        except ValueError:
            return {
                "slope": None,
                "is_valid": False,
                "status": "无效坡度值"
            }

    def parse_traffic_sign_and_signal(self, sign_type, standard="GB 14887"):
        """
        解析交通标志和信号灯信息
        :param sign_type: 标志或信号灯类型
        :param standard: 道路符合标准（默认GB 14887）
        :return: 解析结果字典
        """
        result = {
            "type": sign_type,
            "standard": standard,
            "is_valid": False,
            "status": None,
            "description": None
        }
        
        # 交通标志状态
        if sign_type == "交通标志":
            valid_states = ("交通标志正常", "无交通标志")
            result.update({
                "is_valid": True,
                "status": "正常",
                "description": "道路符合标准：" + standard
            })
        
        # 交通信号灯状态
        elif sign_type == "交通信号灯":
            valid_states = ("交通信号灯正常", "无交通信号灯")
            result.update({
                "is_valid": True,
                "status": "正常",
                "description": "道路符合标准：" + standard
            })
        
        # 无效类型
        else:
            result.update({
                "is_valid": False,
                "status": "无效",
                "description": "未知的交通设施类型"
            })
        
        return result

    def find_road_by_location(self, target_lon, target_lat, radius=0.001):
        """
        根据经纬度查找最近的道路
        :param target_lon: 目标经度
        :param target_lat: 目标纬度
        :param radius: 搜索半径（度）
        :return: 最近的道路信息
        """
        try:
            nearest_road = None
            min_distance = float('inf')
            
            for road in self.root.findall('road'):
                geometry = self._parse_geometry(road)
                if not geometry or "经度" not in geometry or "纬度" not in geometry:
                    continue
                    
                road_lon = float(geometry["经度"])
                road_lat = float(geometry["纬度"])
                
                # 计算距离（使用简单的欧几里得距离）
                distance = ((target_lon - road_lon) ** 2 + 
                           (target_lat - road_lat) ** 2) ** 0.5
                
                # 更新最近的道路
                if distance < min_distance and distance <= radius:
                    min_distance = distance
                    nearest_road = {
                        "道路ID": road.get('id', ''),
                        "距离": distance,
                        "地理坐标": geometry,
                        "道路类型": self._parse_road_type(road),
                        "车道特征": self._parse_lanes(road),
                        "道路设施": self._parse_road_facilities(road),
                        "限速": self._parse_speed_limit(road),
                        "道路表面": self._parse_road_surface(road),
                        "道路几何": self._parse_road_geometry(road)
                    }
            
            return nearest_road
            
        except Exception as e:
            print(f"查找道路错误: {e}")
            return None

    def _parse_geometry(self, road):
        """解析道路几何信息"""
        geometry_data = {
            "坐标点": []
        }
        
        plan_view = road.find('planView')
        if plan_view is not None:
            for geometry in plan_view.findall('geometry'):
                try:
                    # 获取局部坐标
                    x = float(geometry.get('x', '0'))
                    y = float(geometry.get('y', '0'))
                    length = float(geometry.get('length', '0'))
                    heading = float(geometry.get('hdg', '0'))
                    
                    # 转换为WGS84坐标
                    lon, lat = self.coordinate_converter.local_to_wgs84(x, y)
                    
                    if lon is not None and lat is not None:
                        point_data = {
                            "局部坐标": {
                                "x": round(x, 3),
                                "y": round(y, 3)
                            },
                            "地理坐标": {
                                "经度": lon,
                                "纬度": lat
                            },
                            "几何特征": {
                                "长度": round(length, 3),
                                "航向角": round(heading, 3)
                            }
                        }
                        geometry_data["坐标点"].append(point_data)
                
                except (ValueError, TypeError) as e:
                    print(f"[错误] 解析几何数据失败: {e}")
                    continue
        
        # 如果有坐标点，返回第一个点的地理坐标
        if geometry_data["坐标点"]:
            first_point = geometry_data["坐标点"][0]
            return {
                "经度": first_point["地理坐标"]["经度"],
                "纬度": first_point["地理坐标"]["纬度"]
            }
        return {}

    def _parse_road_geometry(self, road):
        """解析道路几何信息"""
        geometry_data = {
            "纵断面坡度": "-1",  # 默认值设为"-1"
            "道路曲率": "-1",
            "道路曲率半径": "-1"
        }
        
        # 解析纵断面坡度信息 (从elevation的b参数获取)
        elevation_profile = road.find('elevationProfile')
        if elevation_profile is not None:
            elevation = elevation_profile.find('elevation')
            if elevation is not None:
                # 使用b参数作为坡度值
                b_param = elevation.get('b', "")
                if b_param:
                    try:
                        # 转换为百分比
                        slope_percent = float(b_param) * 100
                        geometry_data["纵断面坡度"] = str(round(slope_percent, 2))
                    except (ValueError, TypeError):
                        geometry_data["纵断面坡度"] = "-1"
        
        # 解析曲率信息 (从arc的curvature参数获取)
        plan_view = road.find('planView')
        if plan_view is not None:
            # 查找包含arc标签的geometry元素
            for geometry in plan_view.findall('geometry'):
                arc = geometry.find('arc')
                if arc is not None:
                    curvature = arc.get('curvature', "")
                    if curvature:
                        try:
                            # 取绝对值并保留6位小数
                            curvature_value = abs(float(curvature))
                            geometry_data["道路曲率"] = str(round(curvature_value, 6))
                            
                            # 如果曲率不为0，计算曲率半径 (半径 = 1/曲率)
                            if curvature_value > 0:
                                radius = 1.0 / curvature_value
                                geometry_data["道路曲率半径"] = str(round(radius, 2))
                        except (ValueError, TypeError, ZeroDivisionError):
                            pass
                    break  # 找到第一个包含arc标签的geometry后退出
        
        return geometry_data

    def _parse_road_surface(self, road):
        """解析道路表面信息"""
        # 如果没有道路表面信息，返回"-1"
        return "-1"

    def _parse_road_facilities(self, road):
        """解析道路设施信息"""
        facilities_data = {
            "交通标志": "FALSE",
            "交通信号灯": "FALSE"
        }
        
        # 假设 xodr 文件中有相关信息
        signals = road.findall('signals/signal')
        if signals:
            facilities_data["交通信号灯"] = "TRUE"
        
        signs = road.findall('signs/sign')
        if signs:
            facilities_data["交通标志"] = "TRUE"
        
        return facilities_data

    def _parse_speed_limit(self, road):
        """解析道路限速信息"""
        # 遍历所有的 type 标签，寻找其中的 speed 子标签
        for road_type in road.findall('type'):
            speed = road_type.find('speed')
            if speed is not None:
                max_speed = speed.get('max', '')
                unit = speed.get('unit', '')
                if max_speed and unit:
                    return f"{max_speed} {unit}"
        return "-1"  # 如果没有找到限速信息，返回"-1"

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

# 创建解析器实例
parser = OpenDriveParser(file_path)

@app.route('/get_map_data', methods=['GET'])
def get_map_data():
    """
    获取高精地图数据
    :return: JSON 格式的解析结果
    """
    print(f"[信息] API /get_map_data 被调用，使用文件: {file_path}")
    try:
        if not os.path.exists(file_path):
            error_msg = f"地图文件不存在: {file_path}"
            print(f"[错误] {error_msg}")
            return jsonify({"错误信息": error_msg}), 404
            
        map_data = parser.parse()
        if not map_data:
            print("[信息] 无地图数据")
            return jsonify([]), 204
        return jsonify(map_data), 200
    except Exception as e:
        error_msg = f"获取地图数据失败: {e}"
        print(f"[错误] {error_msg}")
        return jsonify({"错误信息": error_msg}), 500

@app.route('/get_road_by_location', methods=['GET'])
def get_road_by_location():
    """
    根据经纬度获取道路信息
    """
    try:
        lon = float(request.args.get('lon', 0))
        lat = float(request.args.get('lat', 0))
        radius = float(request.args.get('radius', 100))
        
        nearby_roads = parser.find_road_by_location(lon, lat, radius)
        
        if not nearby_roads:
            return jsonify({"message": "未找到附近道路"}), 404
            
        return jsonify({
            "查询位置": {
                "经度": lon,
                "纬度": lat
            },
            "搜索半径": radius,
            "道路信息": nearby_roads
        }), 200
        
    except ValueError as e:
        return jsonify({"错误信息": "无效的坐标参数"}), 400
    except Exception as e:
        return jsonify({"错误信息": f"查询失败: {str(e)}"}), 500


# 主程序入口
if __name__ == '__main__':
    print(f"[信息] 启动高精地图 API 服务")
    print(f"[信息] 使用地图文件: {file_path}")
    if not os.path.exists(file_path):
        print(f"[警告] 地图文件不存在: {file_path}")
    app.run(host='127.0.0.1', port=5002, debug=True)
