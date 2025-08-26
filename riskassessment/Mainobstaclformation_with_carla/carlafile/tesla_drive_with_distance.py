import carla
import random
import time
import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.contour import QuadContourSet
from prompt_toolkit.filters import renderer_height_is_known


plt.rcParams['font.sans-serif'] = ['WenQuanYi Zen Hei']
plt.rcParams['axes.unicode_minus'] = False
plt.ion()  # 启用交互模式

current_dr_info = []

# 获取自车相对其他车辆的位置与速度
def get_vehicle_relative_info(world, tesla, detection_range):
    tesla_location = tesla.get_location()
    tesla_velocity = tesla.get_velocity()
    relative_data = []

    for actor in world.get_actors():
        if 'vehicle' in actor.type_id and actor.id != tesla.id:
            other_location = actor.get_location()
            distance = tesla_location.distance(other_location)
            if distance <= detection_range:
                other_velocity = actor.get_velocity()
                posx = other_location.x - tesla_location.x
                posy = other_location.y - tesla_location.y
                relvelx = other_velocity.x - tesla_velocity.x
                relvely = other_velocity.y - tesla_velocity.y
                relative_data.append({
                    'vehicle_id': actor.id,
                    'relative_position': {'posx': posx, 'posy': posy},
                    'relative_velocity': {'relvelx': relvelx, 'relvely': relvely}
                })
    return relative_data

def clear_existing_vehicles(world):
    actors = world.get_actors()
    vehicles = [actor for actor in actors if 'vehicle' in actor.type_id]
    for vehicle in vehicles:
        vehicle.destroy()
        print(f"Destroyed vehicle: {vehicle.id}")
    print("All existing vehicles cleared.")

def check_spawn_position(world, spawn_point, min_distance=3.0):
    for actor in world.get_actors():
        if 'vehicle' in actor.type_id:
            distance = actor.get_location().distance(spawn_point.location)
            if distance < min_distance:
                return False
    return True

def spawn_tesla_model_y(world):
    blueprint_library = world.get_blueprint_library()
    model_y_bp = blueprint_library.find('vehicle.tesla.model3')
    spawn_points = world.get_map().get_spawn_points()
    max_attempts = 10
    for _ in range(max_attempts):
        spawn_point = random.choice(spawn_points)
        if check_spawn_position(world, spawn_point):
            tesla = world.spawn_actor(model_y_bp, spawn_point)
            print(f"Tesla Model Y spawned at {spawn_point.location}")
            return tesla, spawn_point.location
    raise RuntimeError("Failed to find a valid spawn point for Tesla Model Y.")

def find_target_location(world, start_location, min_distance=100):
    spawn_points = world.get_map().get_spawn_points()
    valid_endpoints = [point for point in spawn_points if point.location.distance(start_location) >= min_distance]
    if not valid_endpoints:
        raise RuntimeError("No valid target location found.")
    end_point = random.choice(valid_endpoints)
    print(f"Target location set at {end_point.location}")
    return end_point.location

def calculate_ttc(posx, posy, relvelx, relvely):
    relvel = np.sqrt(relvelx ** 2 + relvely ** 2)
    distance = np.sqrt(posx ** 2 + posy ** 2)
    if relvel == 0:
        TTC = 500
    elif (posy > 4) and (relvely == 0):
        TTC = 501
    else:
        TTC = distance / relvel
        TTC = abs(TTC)
        if TTC > 15:
            TTC = 502
    return TTC

def riskfield111(posx, posy, relvelx, relvely):
    belta_x = 1
    belta_y = 1
    alpha_x = 0.63
    alpha_y = 0.63
    long = 2
    width = 1
    delta_x = belta_x * max(posx - 0.5*long, 0)/(alpha_x * relvelx + 1)
    delta_y = belta_y * max(posy - 0.5 * width, 0) / (alpha_y * relvely + 1)
    delta_risk = math.sqrt(delta_x**2 + delta_y**2)
    if delta_risk == 0:
        delta_risk = 1e-6
    risk_field = 5 / delta_risk
    return risk_field

def riskfield(posx, posy, relvelx, relvely):
    A = 5.0
    k_vx = 50
    k_vy = 30
    alpha = 0.2
    L_obs = 3.0
    relvelx = max(relvelx, 0.1)
    relvely = max(relvely, 0.1)
    sigma_vx = k_vx * (relvelx + 0.0001)
    sigma_vy = k_vy * (relvely + 0.0001)
    numerator = A * np.exp(
        -(posx ** 2 / sigma_vx ** 2) - (posy ** 2 / (sigma_vy ** 2)))
    denominator = 1 + np.exp((posx - alpha * L_obs))
    risk_field = numerator / denominator
    risk_field_max = A

    return risk_field

def update_risk_field(frame, ax, theta, r, posx_grid, posy_grid):
    global current_dr_info
    risk_fields = []
    risk_field_max=5
    for vehicle in current_dr_info:
        risk_field = np.zeros_like(posx_grid)
        for i in range(posx_grid.shape[0]):
            for j in range(posx_grid.shape[1]):
                rel_posx = posx_grid[i, j] - vehicle['relative_position']['posx']
                rel_posy = posy_grid[i, j] - vehicle['relative_position']['posy']
                relvelx = vehicle['relative_velocity']['relvelx']
                relvely = vehicle['relative_velocity']['relvely']
                # 调试输出
                risk_field[i, j] = riskfield(rel_posx, rel_posy, relvelx, relvely)
        risk_fields.append(risk_field)

    if not risk_fields:
        combined_risk_field = np.zeros_like(posx_grid)
    else:
        combined_risk_field = np.max(risk_fields, axis=0)

    combined_risk_field = np.clip(combined_risk_field, 0, risk_field_max)
    combined_risk_field = np.round(combined_risk_field, decimals=6)
    for c in ax.collections:
        if isinstance(c, QuadContourSet):  # 使用全局导入的 QuadContourSet
            c.remove()

    # 绘制风险场
    contour = ax.contourf(theta, r, combined_risk_field, cmap='Reds', levels=np.linspace(0, risk_field_max, 256))
    contour.set_clim(0, risk_field_max)
    # # 创建颜色条
    # cbar = plt.colorbar(contour, ax=ax, label='风险值')
    # cbar.set_ticks(np.linspace(0, 5, 6))
    return (contour,)


def radio_picture(detection_range):
    global current_dr_info
    risk_field_max=5
    theta = np.linspace(0, 2 * np.pi, 100)
    r = np.linspace(0, detection_range, 100)
    theta, r = np.meshgrid(theta, r)
    posx_grid = r * np.cos(theta)
    posy_grid = r * np.sin(theta)
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    ax.set_rlabel_position(0)

    # 初始状态：风险值为 0
    combined_risk_field = np.zeros_like(posx_grid)

    # 绘制风险场
    contour = ax.contourf(theta, r, combined_risk_field, cmap='Reds', levels=np.linspace(0, risk_field_max, 256))
    contour.set_clim(0, risk_field_max)
    # 创建颜色条
    cbar = plt.colorbar(contour, ax=ax, label='风险值')
    cbar.set_ticks(np.linspace(0, risk_field_max, 6))  # 设置刻度为 0, 1, 2, 3, 4, 5
    plt.title('风险场雷达图')
    ani = animation.FuncAnimation(
        fig, update_risk_field, fargs=(ax, theta, r, posx_grid, posy_grid),
        interval=100, blit=False, repeat=True, cache_frame_data=False
    )
    return fig, ani

def drive_to_target(tesla, world, target_location):
    global current_dr_info
    tesla.set_autopilot(True)
    count = 0
    detection_range = 30.0
    fig, ani = radio_picture(detection_range)
    while True:
        count += 1
        world.tick()
        current_location = tesla.get_location()
        distance_to_target = math.sqrt(
            (current_location.x - target_location.x) ** 2 +
            (current_location.y - target_location.y) ** 2
        )
        if count % 10 == 0:
            dr_info = get_vehicle_relative_info(world, tesla, detection_range)
            current_dr_info = dr_info
            if not dr_info:
                print(f"自车周围{detection_range:.2f}m内无道路参与者")
            else:
                risk_list = []
                for target in dr_info:
                    ax = fig.axes[0]
                    for line in ax.lines:
                        line.remove()
                    risk_dist = {}
                    posx = target['relative_position']['posx']
                    posy = target['relative_position']['posy']
                    relvelx = target['relative_velocity']['relvelx']
                    relvely = target['relative_velocity']['relvely']
                    TTC = calculate_ttc(posx, posy, relvelx, relvely)
                    risk_dist['vehicle_id'] = target['vehicle_id']
                    risk_dist['TTC'] = round(TTC, 3)
                    risk_list.append(risk_dist)
                sorted_list = sorted(risk_list, key=lambda x: (x['TTC']))
                most_interesting = sorted_list[0]
                print(f"当前最能威胁到自车的车辆id为{most_interesting['vehicle_id']},TTC值为{most_interesting['TTC']}")
        if count % 50 == 0:
            print(f"Distance to target: {distance_to_target:.2f} meters")
        if distance_to_target < 5.0:
            print("Tesla Model Y has reached the target location.")
            break
        time.sleep(0.001)
        spectator = world.get_spectator()
        # 使用 tesla 保持一致
        follow_tesla_with_spectator(world, tesla, spectator)
        plt.pause(0.0001)
    plt.close(fig)

def follow_tesla_with_spectator(world, tesla, spectator, height=70, pitch=-90):
    # 使用 tesla 获取位置和朝向
    transform = tesla.get_transform()
    spectator.set_transform(carla.Transform(transform.location + carla.Location(z=height), carla.Rotation(pitch=pitch)))

def main():
    client = carla.Client('localhost', 2000)
    client.set_timeout(10.0)
    world = client.get_world()
    clear_existing_vehicles(world)
    tesla, start_location = spawn_tesla_model_y(world)
    target_location = find_target_location(world, start_location)
    drive_to_target(tesla, world, target_location)
    clear_existing_vehicles(world)
    print("Simulation complete.")

if __name__ == '__main__':
    main()