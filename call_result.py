import requests
import time


#这个代码运行是将ODD元素保存到本地


# 定义接口的 URL
url = "http://127.0.0.1:5009/get_results"

# 循环调用接口，每隔1秒调用一次
while True:
    try:
        # 发送 POST 请求
        response = requests.get(url)

        # 检查响应状态码
        if response.status_code == 200:
            data = response.json()
            print("接口返回的数据：")
            print(data)
        else:
            print(f"接口调用失败，状态码：{response.status_code}")
            print(f"响应内容：{response.text}")
    except Exception as e:
        print(f"发生错误：{e}")
        print("请检查接口地址的合法性或网络连接是否正常。")

    # 每隔1秒调用一次
    time.sleep(5)