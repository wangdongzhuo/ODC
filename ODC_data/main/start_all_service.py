import os
import subprocess
import time
import signal

def get_root_path():
    """
    获取ODCSOFT_KINGLONG的根路径
    """
    current_path = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件的绝对路径
    root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))  # 向上回溯三层到根目录
    return root_path
# api_service.py 和 call_api.py 文件所在目录
root_path = get_root_path()
api_directory = os.path.join(root_path, "monitorODC\\ODC_data\\main")  # 更新为你的实际路径
# 要启动的服务文件名列表
service_files = [
    "api_service_CAN.py",
    "api_service_driver.py",
    # "CAN_api_0305.py",
    # "driver_api.py",
    "api_service_cloud.py",
    "api_service_HDmap.py",
    "Api_weather.py",
    "api_service_channel.py"
]

call_simu_api_files = [
    "simulate_real_time_data_CAN.py",
    "simulate_real_time_data_driver.py"
    # 可以继续添加其他服务文件...
]

call_api_files = [
    "call_api_CAN.py",
    "call_api_driver.py",
    # "CAN_call_0305.py",
    # "driver_call.py",
    "call_api_cloud.py",
    "call_api_HDmap.py"
    "call_channel.py"
    "call_api_traffic.py",
]

def start_service(file_name):
    """启动 Flask API 服务并返回子进程对象"""
    file_path = os.path.join(api_directory, file_name)
    if os.path.exists(file_path):
        print(f"[信息] 启动 {file_name} 服务...")
        process = subprocess.Popen(["python", file_path], cwd=api_directory)
        time.sleep(2)  # 延时确保服务已启动
        return process
    else:
        print(f"[警告] {file_name} 文件不存在！")
        return None


def start_all_services():
    """启动所有服务并返回子进程列表"""
    processes = []
    print("[信息] 启动所有 API 服务...")

    # 启动 api_service 文件
    for service_file in service_files:
        process = start_service(service_file)
        if process:
            processes.append(process)

    for call_simu_api_file in call_simu_api_files:
        process = start_service(call_simu_api_file)
        if process:
            processes.append(process)

    # 启动 call_api 文件
    for call_api_file in call_api_files:
        process = start_service(call_api_file)
        if process:
            processes.append(process)


    print("[信息] 所有服务已启动！")
    return processes


def signal_handler(sig, frame):
    """处理Ctrl+C信号"""
    print("\n[信息] 接收到Ctrl+C，正在停止所有服务...")
    for process in processes:
        process.terminate()  # 终止子进程
        process.wait()  # 等待子进程结束
    print("[信息] 所有服务已停止。")
    os._exit(0)


if __name__ == '__main__':
    processes = start_all_services()
    # 注册信号处理函数
    signal.signal(signal.SIGINT, signal_handler)
    # 主进程保持运行
    while True:
        time.sleep(1)
