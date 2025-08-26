import requests
import json
import time

def call_driver_state_api():
    """调用驾驶员状态监测 API 并格式化输出结果"""
    url = "http://127.0.0.1:5003/get_driver_state"
    last_state = None

    while True:
        try:
            # print("\n[信息] 正在获取驾驶员状态...")
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # 如果状态发生变化，则输出详细信息
                if data != last_state:
                    # print("[信息] 检测到状态变化:")
                    # print(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(data['timestamp']))}")
                    # print(f"原始帧: {data['raw_frame']}")
                    # print("\n[状态帧解析]")
                    # frame = data['frame']
                    # print(f"帧头(head): {frame['head']}")
                    # print(f"命令字(cmd): {frame['cmd']}")
                    # print(f"数据长度(length): {frame['length']}")
                    # print(f"数据内容(data): {frame['data']}")
                    # print(f"校验和(check): {frame['check']}")
                    # print(f"帧尾(tail): {frame['tail']}")
                    # print(f"\n状态码: {data['state_code']}")
                    # print(f"状态描述: {data['state_description']}")
                    
                    # 检查是否有异常状态
                    # if data['state_code'] != '0x00':
                        # print(f"\n[警告] 检测到异常驾驶行为：{data['state_description']}")
                    
                    last_state = data
                    return last_state
            elif response.status_code == 404:
                print("[警告] 暂无状态数据")
            else:
                print(f"[错误] 收到意外的状态码 {response.status_code}")
                
        except requests.exceptions.ConnectionError:
            print("[错误] 无法连接到服务器，请确保服务器已启动")
        except Exception as e:
            print(f"[错误] 调用 API 时发生异常: {str(e)}")

        time.sleep(2)  # 每2秒检测一次

if __name__ == "__main__":
    print("[信息] 启动驾驶员状态监测客户端...")
    call_driver_state_api()