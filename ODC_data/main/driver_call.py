import requests
import time


def call_driver_state_api():
    """调用驾驶员状态监测 API 并格式化输出结果"""
    url = "http://127.0.0.1:5003/get_driver_state"  # 你的 API 服务地址
    last_state = None

    while True:
        try:
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json()

                # 如果状态发生变化，且状态码为非 0x00（异常状态），则输出
                if data != last_state:
                    if data['state_code'] != '0x00':  # 检查是否是异常状态
                        print("[警告] 检测到异常驾驶行为:")
                        print(f"状态码: {data['state_code']}")
                        print(f"状态描述: {data['state_description']}")

                    last_state = data
            elif response.status_code == 404:
                print("[警告] 暂无状态数据")
            else:
                print(f"[错误] 收到意外的状态码 {response.status_code}")

        except requests.exceptions.ConnectionError:
            print("[错误] 无法连接到服务器，请确保服务器已启动")
        except Exception as e:
            print(f"[错误] 调用 API 时发生异常: {str(e)}")

        time.sleep(0.05)  # 每2秒检测一次


if __name__ == "__main__":
    call_driver_state_api()
