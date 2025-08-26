import requests

def get_event_info():
    url = 'http://127.0.0.1:5004/get_event_info'
    try:
        response = requests.get(url)

        if response.status_code == 200:
            # 解析并打印返回的中文解读数据
            data = response.json()
            return data
            # # 输出所有事件数据
            # print("API 返回的事件信息解读：")
            # for event in data:
            #     print(f"\n事件ID: {event['事件ID']}")
            #     print(f"车辆ID: {event['车辆ID']}")
            #     print(f"事件类型: {event['事件类型']}")
            #     print(f"事件优先级: {event['事件优先级']}")
            #     print(f"预计速度: {event['预计速度']}")
            #     print(f"最大速度: {event['最大速度']}")
            #     print(f"最小速度: {event['最小速度']}")
            #     print(f"交叉口数量: {event['交叉口数量']}")
            #     print(f"行为类型: {event['行为类型']}")
            #     print(f"与停止线的距离: {event['与停止线的距离']}")
            #     print(
            #         f"事件位置: 纬度={event['事件位置']['纬度']} 经度={event['事件位置']['经度']} 海拔={event['事件位置']['海拔']}")
            #     print(f"事件发生时间戳: {event['事件发生时间戳']}")
            #     print(f"UUID: {event['UUID']}")
        else:
            print(f"Error: {response.status_code}")
            print("错误详情:", response.text)  # 输出错误详情

    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")

# 主程序执行
if __name__ == '__main__':
    get_event_info()
