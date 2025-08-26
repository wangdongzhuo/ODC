
from tesla_drive_with_distance import *

def clear_scene(world):
    # 获取当前场景中的所有演员（包括车辆和传感器）
    actors = world.get_actors()

    # 遍历所有演员，销毁车辆和传感器
    for actor in actors:
        # 车辆类型判断（可以根据需要修改匹配类型）
        if 'vehicle' in actor.type_id:
            actor.destroy()
            print(f"Destroyed vehicle: {actor.id}")
        # 传感器类型判断
        elif 'sensor' in actor.type_id:
            actor.destroy()
            print(f"Destroyed sensor: {actor.id}")

    print("Scene cleared of all vehicles and sensors.")

collision_report = []

def setup_environment():
    # 连接到 Carla 服务器（本地或远程）
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()

    # 设置天气（可以根据需要调整）
    weather = carla.WeatherParameters.ClearNoon
    world.set_weather(weather)

    return client, world

def check_spawn_position(world, spawn_point):
    # 检查生成点是否有碰撞
    for actor in world.get_actors():
        # 如果生成点与任何物体的距离小于 1.0，认为发生了碰撞
        if actor.get_location().distance(spawn_point.location) < 1.0:
            return False
    return True

collision_sensors = []

def add_collision_sensor(vehicle, world):
    # 创建一个碰撞传感器并附加到车辆上
    collision_sensor_bp = world.get_blueprint_library().find('sensor.other.collision')
    collision_sensor = world.spawn_actor(collision_sensor_bp, carla.Transform(), attach_to=vehicle)

    # 定义碰撞回调函数
    def on_collision(event):
        global collision_report
        actor = event.other_actor
        collision_location = vehicle.get_location()  # 使用车辆的当前位置作为碰撞点
        normal_impulse = event.normal_impulse  # 获取碰撞的冲击力

        # 记录碰撞事件
        collision_report.append({
            'vehicle': vehicle.id,
            'collided_with': actor.id,
            'collision_location': collision_location,
            'normal_impulse': normal_impulse,
            'timestamp': world.get_snapshot().timestamp
        })
        print(
            f"Collision detected! Vehicle {vehicle.id} collided with {actor.id} at {collision_location} with normal impulse {normal_impulse}")

    collision_sensor.listen(on_collision)

    # 将传感器添加到传感器列表中
    collision_sensors.append(collision_sensor)
    return collision_sensor

def cleanup_sensors():
    global collision_sensors
    for sensor in collision_sensors:
        if sensor.is_alive:
            sensor.destroy()
    collision_sensors.clear()
    print("All collision sensors destroyed.")

def setup_traffic_flow_with_collision(client, world, num_vehicles=40, min_distance=1.0, max_attempts=5):
    blueprint_library = world.get_blueprint_library()
    vehicle_bp = blueprint_library.filter('vehicle.*')
    vehicles = []

    spawn_points = world.get_map().get_spawn_points()

    for _ in range(num_vehicles):
        attempts = 0
        vehicle_spawned = False

        # 多次尝试生成车辆
        while attempts < max_attempts and not vehicle_spawned:
            spawn_point = random.choice(spawn_points)
            if check_spawn_position(world, spawn_point):
                # Spawn vehicle and add collision sensor
                vehicle = world.spawn_actor(random.choice(vehicle_bp), spawn_point)
                vehicles.append(vehicle)
                add_collision_sensor(vehicle, world)  # Add collision sensor to the vehicle

                # Wait until all vehicles are spawned
                vehicle_spawned = True
            else:
                attempts += 1
                print(f"Attempt {attempts}: Spawn point {spawn_point.location} is blocked, retrying...")

        if not vehicle_spawned:
            print(f"Failed to spawn vehicle after {max_attempts} attempts.")

    # Once all vehicles are spawned, set them to autopilot mode
    for vehicle in vehicles:
        vehicle.set_autopilot(True)

    return vehicles

def main():
    client, world = setup_environment()

    # 清理场景中的所有车辆和传感器
    clear_scene(world)

    # 创建交通流并确保所有车辆加载完毕后才开始运动
    tesla, start_location = spawn_tesla_model_y(world)
    target_location = find_target_location(world, start_location)
    vehicles = setup_traffic_flow_with_collision(client, world, num_vehicles=30, min_distance=1.0)
    drive_to_target(tesla, world, target_location)
    clear_existing_vehicles(world)
    print("Simulation complete.")
    try:
        while True:
            world.tick()
            # Optionally, report collisions after each tick
            if collision_report:
                for report in collision_report:
                    print(f"Collision report: Vehicle {report['vehicle']} collided with {report['collided_with']} at {report['collision_location']} at {report['timestamp']}")
                # Clear the report after handling
                collision_report.clear()
    finally:
        # 清理所有生成的车辆和传感器
        for vehicle in vehicles:
            if vehicle.is_alive:
                vehicle.destroy()
        cleanup_sensors()  # 确保销毁所有传感器
        print("All vehicles and sensors destroyed.")

if __name__ == '__main__':
    main()