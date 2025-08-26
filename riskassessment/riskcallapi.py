import requests
import time
import base64
from io import BytesIO
import matplotlib.pyplot as plt
from matplotlib.image import imread
import cv2
import threading

# 使用了 requests 库来发起HTTP请求，使用 time 库来控制请求的频率
# 接口URL
url = 'http://127.0.0.1:5009/risk_value'
video_url = 'http://127.0.0.1:5010/video_feed'  # 视频流接口

# 调用接口的函数
def call_api():
    response = requests.get(url)  # 通过GET请求向指定的URL发送请求。返回值存储在 response 中，包含了API返回的数据和状态。
    if response.status_code == 200:  # 检查HTTP响应的状态码是否为200，200代表请求成功。如果是200，则说明API请求成功，接下来会处理返回的数据。
        data = response.json()
        # 打印各个值
        print(data)
        system_risk = data.get('system_risk', '未获取到风险值')
        driving_risk = data.get('driving_risk', '未获取到行车风险')
        TTC = data.get('TTC', '未获取到TTC值')
        num_level = data.get('num_level', '未获取到风险等级')
        str_level = data.get('str_level', '未获取到动态驾驶风险等级')
        driving_mode = data.get('driving_mode', '未获取到驾驶模式信息')
    else:
        print("Failed to retrieve data:", response.status_code)

def display_video_stream():
    print("Starting video stream thread...")
    # 初始化视频流捕获
    cap = cv2.VideoCapture(video_url)
    if not cap.isOpened():
        print("无法打开视频流，请检查 /video_feed 是否正常运行")
        return

    while True:
        ret, frame = cap.read()  # 读取视频帧
        if not ret:
            print("视频流读取失败，尝试重新连接...")
            cap.release()
            cap = cv2.VideoCapture(video_url)  # 尝试重新打开
            time.sleep(1)  # 等待1秒后重试
            continue

        # 显示视频帧
        cv2.imshow('风险场雷达视频流', frame)

        # 按 'q' 键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 清理资源
    cap.release()
    cv2.destroyAllWindows()

# 设置调用频率，例如每10秒调用一次
interval = 1  # 1 seconds

# 启动视频流显示（在新线程中运行，避免阻塞主循环）
video_thread = threading.Thread(target=display_video_stream, daemon=True)
video_thread.start()
# print("Video thread started:", video_thread.is_alive())
if __name__ == "__main__":
    while True:
        try:
            call_api()
            # display_video_stream()
        except KeyboardInterrupt:
            print("程序被用户中断")
            break
        except Exception as e:
            continue
        finally:
            time.sleep(interval)