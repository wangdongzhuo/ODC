import requests
import time

def get_channel_state():
    try:
        # 调用接口获取监控数据
        response = requests.get('http://127.0.0.1:4999/get_channel_state')
        data = response.json()
        # print(data)
        # print(type(data))
        # # 打印监控数据
        # print("\n=== 通道监控数据 ===")
        # print(f"总数据包数: {data['total_packets']}")
        # print(f"丢包数: {data['lost_packets']}")
        # print(f"最新延迟: {data['latest_latency']:.3f}秒" if data['latest_latency'] else "最新延迟: 无数据")
        # print(f"最新丢包率: {data['latest_loss_rate']:.2f}%")
        # print(f"最近数据包历史: {data['packet_history']}")
        # print("==================\n")
        return data
        
    except requests.exceptions.ConnectionError:
        print("错误：无法连接到服务器，请确保服务器正在运行。")
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    print("开始监控通道状态...")
    while True:
        get_channel_state()
        time.sleep(1)  # 每秒更新一次