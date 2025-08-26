import requests

# 定义 Flask API 的 URL
api_url = "http://127.0.0.1:5002/get_data"

def get_weather_data():
    try:
        # 发送 GET 请求
        response = requests.get(api_url)
        
        # 检查响应状态码
        if response.status_code == 200:
            data = response.json()  # 解析 JSON 响应
            print("天气数据:")
            print(data)
            return data
        else:
            print(f"请求失败，状态码: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"请求出错: {e}")

if __name__ == "__main__":
    # 调用 API 获取数据
    get_weather_data()
