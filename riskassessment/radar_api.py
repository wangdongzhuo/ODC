from flask import Flask, jsonify, Response
import numpy as np
import requests
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.contour import QuadContourSet
import cv2
from prompt_toolkit.filters import renderer_height_is_known
import math
import base64
from io import BytesIO
import time
import io
from enum import Enum

app = Flask(__name__)

current_dr_info = []
posx = 30 
posy = 5 
relvelx = 6 
relvely = 2

def RiskField_radio(rel_posx,rel_posy):
    global relvelx
    A = 5.0
    kv = 0.5  # 调整为更小的值
    alpha = 0.2
    L_obs = 5.0
    # if not hasattr(Mainobstaclformation, 'relvelx') or not  launchstate:
    #     print("Mainobstaclformation 未初始化或无主目标")
    #     return 0.0
    sigma_v = kv * np.abs( relvelx)
    sigma_y = 0.5  # 调整为更小的值
    relv = -1 if  relvelx < 0 else 1
    numerator = A * np.exp(
        -(rel_posx ** 2 / sigma_v ** 2) - (rel_posy ** 2 / (sigma_y ** 2)))
    denominator = 1 + np.exp(relv * (rel_posy - alpha * L_obs * relv))
    vehicle_risk = numerator / denominator
    return vehicle_risk

def Update_Risk_Field(frame, ax, theta, r, posx_grid, posy_grid):
    global posx, posy
    risk_fields = []
    risk_field_max = 5.0

    # 检查 Mainobstaclformation 是否有效
    # if not hasattr(Mainobstaclformation, 'launchstate') or not  launchstate:
    #     combined_risk_field = np.zeros_like(posx_grid)
    #     # print("No valid Mainobstaclformation data")
    # else:
        # print(" posx:",  posx)
        # print(" relvelx:",  relvelx)
    risk_field = np.zeros_like(posx_grid)
    # print("Calculating risk field...")
    for i in range(posx_grid.shape[0]):
        for j in range(posx_grid.shape[1]):
            rel_posx = posx_grid[i, j] -  posx
            rel_posy = posy_grid[i, j] -  posy
            risk_field[i, j] = RiskField_radio(rel_posx, rel_posy)
    risk_fields.append(risk_field)
    combined_risk_field = np.max(risk_fields, axis=0)
    # print("Max risk field value:", np.max(combined_risk_field))

    # 限制风险值范围
    combined_risk_field = np.clip(combined_risk_field, 0, risk_field_max)
    combined_risk_field = np.round(combined_risk_field, decimals=6)

    # 清除旧的轮廓图
    for c in ax.collections:
        if isinstance(c, QuadContourSet):
            c.remove()

    # 绘制新轮廓图
    contour = ax.contourf(theta, r, combined_risk_field, cmap='Reds', levels=np.linspace(0, risk_field_max, 256))
    contour.set_clim(0, risk_field_max)
    return (contour,)

def Generate_Radio_Frame(detection_range):
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw={'projection': 'polar'})
    try:
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        theta = np.linspace(0, 2 * np.pi, 100)
        r = np.linspace(0, detection_range, 100)
        theta, r = np.meshgrid(theta, r)
        posx_grid = r * np.cos(theta)
        posy_grid = r * np.sin(theta)

        plt.rcParams['font.sans-serif'] = ['SimHei']
        plt.rcParams['axes.unicode_minus'] = False
        ax.set_rlabel_position(0)

        # 初始化空的轮廓图
        risk_field_max = 5
        contour = ax.contourf(theta, r, np.zeros_like(posx_grid), cmap='Reds',
                              levels=np.linspace(0, risk_field_max, 256))
        contour.set_clim(0, risk_field_max)

        # 更新风险场
        Update_Risk_Field(0, ax, theta, r, posx_grid, posy_grid)

        cbar = plt.colorbar(contour, ax=ax, label='风险值')
        cbar.set_ticks(np.linspace(0, risk_field_max, 6))
        plt.title('风险场雷达图')

        buf = BytesIO()
        plt.savefig(buf, format='png', bbox_inches='tight')
        buf.seek(0)
        img = cv2.imdecode(np.frombuffer(buf.getvalue(), np.uint8), cv2.IMREAD_COLOR)
        return img
    finally:
        plt.close(fig)
        plt.close("all")

def generate_video_stream(detection_range=30):
    while True:
        try:
            frame = Generate_Radio_Frame(detection_range)
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret:
                print("帧编码失败")
                continue
            frame_data = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_data + b'\r\n')
            time.sleep(0.1)
        except Exception as e:
            print(f"生成视频流时出错: {e}")
            break

@app.route('/video_feed')
def video_feed():
    print("Received /video_feed request")
    return Response(generate_video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__  == "__main__":
    app.run(host='127.0.0.1', port=5010,
            debug=True)