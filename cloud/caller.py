import requests

# 定义接口的 URL
url = "http://127.0.0.1:5001/get_data"

try:
    # 发送 GET 请求
    response = requests.get(url)
    
    # 检查响应状态码
    if response.status_code == 200:
        # 获取并解析 JSON 数据
        data = response.json()
        print("接口返回的数据：")
        print(data)
    else:
        print(f"请求失败，状态码：{response.status_code}")
except Exception as e:
    print(f"发生错误：{e}")
