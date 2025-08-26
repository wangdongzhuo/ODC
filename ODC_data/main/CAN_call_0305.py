import requests
import json
import time  # 用于循环定时

def call_api():
    url = "http://0.0.0.0:5001/get_can_data"
    last_data = None  # 用于记录上一次的返回数据

    while True:  # 持续循环调用 API
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                # 如果数据和上次相同，则跳过输出
                if data != last_data:
                    print("New Data:")
                    print(json.dumps(data, indent=4, ensure_ascii=False))  # 格式化输出 JSON 数据
                    last_data = data  # 更新记录的上一次数据
            elif response.status_code == 204:
                # 无新数据时，可以选择打印提示（可选）
                print("No new data available.")
            else:
                print(f"Error: Received unexpected status code {response.status_code}")
        except Exception as e:
            print(f"[Error] Exception while calling API: {e}")

        # 每隔 1 秒请求一次 API
        time.sleep(1)

if __name__ == "__main__":
    call_api()
