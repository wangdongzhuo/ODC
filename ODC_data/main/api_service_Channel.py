from flask import Flask, jsonify
import ping3
import threading
import time
from collections import deque

app = Flask(__name__)
monitoring_data = {
    "total_packets": 0,
    "lost_packets": 0,
    "latest_latency": None,
    "latest_loss_rate": 0.0,
    "window_size": 10,  # 滑动窗口大小
    "packet_history": deque(maxlen=10)  # 用于存储最近的丢包情况
}

# 监控线程
def monitor_task(host, interval=1, timeout=2):
    global monitoring_data
    while True:
        # 使用 ping 函数时直接设置超时时间
        response = ping3.ping(host, timeout=timeout)
        monitoring_data["total_packets"] += 1
        if response is None:
            monitoring_data["lost_packets"] += 1
            monitoring_data["packet_history"].append(1)  # 1 表示丢包
        else:
            monitoring_data["latest_latency"] = response
            monitoring_data["packet_history"].append(0)  # 0 表示成功

        # 计算滑动窗口内的丢包率
        window_lost_packets = sum(monitoring_data["packet_history"])
        window_total_packets = len(monitoring_data["packet_history"])
        monitoring_data["latest_loss_rate"] = (window_lost_packets / window_total_packets) * 100 if window_total_packets > 0 else 0.0

        time.sleep(interval)



@app.route('/get_channel_state', methods=['GET'])
def get_channel_state():
    monitoring_data["packet_history"] = list(monitoring_data["packet_history"])
    return jsonify(monitoring_data)


if __name__ == '__main__':
    # 启动监控任务
    target_ip = "36.133.111.135"  # 替换为目标 IP 地址
    interval = 1  # 每秒监控一次
    timeout = 2  # 超时时间为2秒
    threading.Thread(target=monitor_task, args=(target_ip, interval, timeout), daemon=True).start()
    # 启动 Flask 应用
    app.run(host='127.0.0.1', port=4999,debug=True)