import redis
import sys
import os

# 添加模块搜索路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'Define_pb2'))

# 从Define_pb2目录导入pb2文件
import location_pb2
import mmobstacles_pb2
import lanelist_pb2
import trafficlightlist_pb2

# 创建 Redis 客户端
r = redis.Redis(host='127.0.0.1', port=6379, db=0)

# 从 Redis 中获取各类 Protobuf 数据
location_data = r.get('Sensor_Location')
obstacle_data = r.get('Sensor_Mmobstacles')  # 更新为正确的key
lanelist_data = r.get('Sensor_Lanelist')  # 更新为正确的key
trafficlight_data = r.get('Sensor_Trafficlightlist')  # 更新为正确的key

# 修改错误提示消息
if not location_data:
    print("\n未找到键 'Sensor_Location' 或数据为空")
if not obstacle_data:
    print("\n未找到键 'Sensor_Mmobstacles' 或数据为空")
if not lanelist_data:
    print("\n未找到键 'Sensor_Lanelist' 或数据为空")
if not trafficlight_data:
    print("\n未找到键 'Sensor_Trafficlightlist' 或数据为空")

if location_data:
    location = location_pb2.Location()
    location.ParseFromString(location_data)
    print("\n=== Location Data ===")
    print(f"时间戳: {location.timestamp}")
    print(f"经度: {location.lon}")
    print(f"纬度: {location.lat}")
    print(f"高程: {location.height}")
    print(f"俯仰角: {location.pitch}")
    print(f"横滚角: {location.roll}")
    print(f"航向角: {location.heading}")
    print(f"线速度矢量: {location.linear_velocity}")
    print(f"线速度x方向分量: {location.velocity_x}")
    print(f"线速度y方向分量: {location.velocity_y}")
    print(f"线速度z方向分量: {location.velocity_z}")
    print(f"线加速度矢量: {location.linear_acceleration}")
    print(f"线加速度分量_x: {location.acceleration_x}")
    print(f"线加速度分量_y: {location.acceleration_y}")
    print(f"线加速度分量_z: {location.acceleration_z}")
    print(f"角速度矢量: {location.angular_velocity}")
    print(f"角速度分量_x: {location.angular_velocity_x}")
    print(f"角速度分量_y: {location.angular_velocity_y}")
    print(f"角速度分量_z: {location.angular_velocity_z}")
    print(f"参考点经度: {location.origin_lon}")
    print(f"参考点纬度: {location.origin_lat}")
    print(f"相对参考点 x 坐标: {location.utm_position_x}")
    print(f"相对参考点 y 坐标: {location.utm_position_y}")
    print(f"相对参考点 z 坐标: {location.utm_position_z}")

if obstacle_data:
    mmobstacles = mmobstacles_pb2.MMobstacles()
    mmobstacles.ParseFromString(obstacle_data)
    
    print("\n=== Obstacle Data ===")
    print(f"时间戳: {mmobstacles.timestamp}")
    print(f"障碍物数量: {mmobstacles.obstacle_num}")
    
    for i, obstacle in enumerate(mmobstacles.obstacles):
        print(f"\n障碍物 {i+1}:")
        print(f"障碍物 ID: {obstacle.id}")
        print(f"车辆坐标系下中心点位置 x 坐标: {obstacle.center_pos_vehicle_x}")
        print(f"车辆坐标系下中心点位置 y 坐标: {obstacle.center_pos_vehicle_y}")
        print(f"车辆坐标系下中心点位置 z 坐标: {obstacle.center_pos_vehicle_z}")
        print(f"世界坐标系下中心点位置 x 坐标: {obstacle.center_pos_abs_x}")
        print(f"世界坐标系下中心点位置 y 坐标: {obstacle.center_pos_abs_y}")
        print(f"世界坐标系下中心点位置 z 坐标: {obstacle.center_pos_abs_z}")
        print(f"车辆坐标系下速度: {obstacle.velocity_vehicle}")
        print(f"世界坐标系下速度: {obstacle.velocity_abs}")
        print(f"车辆坐标系下航向角: {obstacle.theta_vehicle}")
        print(f"世界坐标系下航向角: {obstacle.theta_abs}")
        print(f"障碍物长度: {obstacle.length}")
        print(f"障碍物宽度: {obstacle.width}")
        print(f"障碍物高度: {obstacle.height}")
        print(f"障碍物类别: {obstacle.type}")
        print(f"障碍物类别置信度: {obstacle.confidence}")
        print(f"车道线位置: {obstacle.lane_position}")
        print(f"融合障碍物来源标识: {obstacle.fusion_type}")
        print(f"路口编号: {obstacle.cross_id}")
        print(f"源类型: {obstacle.src_type}")
        print(f"车道编号: {obstacle.lane_id}")
        print(f"车道序列号: {obstacle.lane_index}")

if lanelist_data:
    lanelist = lanelist_pb2.LaneList()
    lanelist.ParseFromString(lanelist_data)
    
    print("\n=== LaneList Data ===")
    print(f"时间戳: {lanelist.timestamp}")
    print(f"车道线数量: {lanelist.lane_num}")
    
    for i, line in enumerate(lanelist.laneline):
        print(f"\n车道线 {i+1}:")
        print(f"车道线类型: {line.lane_type}")
        print(f"车辆坐标系点数量: {line.pts_vehicle_num}")
        print(f"世界坐标系点数量: {line.pts_abs_num}")
        print(f"车道线置信度: {line.confidence}")
        
        print("\n车辆坐标系下的点集:")
        for j, pt in enumerate(line.pts_vehicle):
            print(f"  点 {j+1}: x={pt.x}, y={pt.y}")
            
        print("\n世界坐标系下的点集:")
        for j, pt in enumerate(line.pts_abs):
            print(f"  点 {j+1}: x={pt.x}, y={pt.y}")

if trafficlight_data:
    trafficlightlist = trafficlightlist_pb2.TrafficLightlist()
    trafficlightlist.ParseFromString(trafficlight_data)
    
    print("\n=== TrafficLight Data ===")
    print(f"时间戳: {trafficlightlist.timestamp}")
    print(f"交通灯数量: {trafficlightlist.traffic_light_num}")
    
    for i, light in enumerate(trafficlightlist.trafficlights):
        print(f"\n交通灯 {i+1}:")
        print(f"交通灯颜色类型: {light.color}")
        print(f"交通灯检测置信度: {light.confidence}")
        print(f"交通灯矩形框左上角 x 坐标: {light.light_pt_x}")
        print(f"交通灯矩形框左上角 y 坐标: {light.light_pt_y}")
        print(f"交通灯矩形框高度: {light.height}")
        print(f"交通灯矩形框宽度: {light.width}") 