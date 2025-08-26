import requests
import time

# 调用本地API接口

while True:
    try:
        response = requests.get("http://127.0.0.1:5005/get_data")
        if response.status_code == 200:
            weather_data = response.json()
            print(weather_data)
        else:
            print(f"请求失败，状态码：{response.status_code}")
        time.sleep(1)
    except:
        print("未启动API服务")
        time.sleep(2)
        continue
