import os
import sys
import signal
import subprocess
import time

def main():
    # 自动获取根路径
    root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # 获取到工作区间根路径
    # 预定义启动模式配置
    modes = {
        1: {
            "description": "模式1: 本地保存", # 时隔几分钟/秒会删除文件
            "files": ["monitorODC\ODC_data\main\start_all_service.py",
                       "monitorODC\call_monitor_service.py",
                       "monitorODC\get_odd_api_dynamic.py",
                       "monitorODC\save_odd_to_device_api.py"]
        },
        2: {
            "description": "模式2: 云端上传", # 将数据上传到云端 (正常运行模式)
            "files": ["monitorODC\ODC_data\main\start_all_service.py",
                       "monitorODC\call_monitor_service.py",
                       "monitorODC\get_odd_api_dynamic.py",
                       "monitorODC\save_odd_to_device_api.py",
                       "monitorODC\send2cloud\send_cloud_ODC.py"]
        },
        3: {
            "description": "模式3: 风险调试",
            "files": ["monitorODC\ODC_data\main\start_all_service.py",
                       "monitorODC\call_monitor_service.py",
                       "monitorODC\get_odd_api_dynamic.py",
                       "monitorODC\save_odd_to_device_api.py",
                       "monitorODC\\riskassessment\\riskcallapi.py"]
        }
    }

    # 获取用户输入
    try:
        choice = 1 # 对应输出模式的序号
        if choice not in modes:
            raise ValueError
    except:
        print("无效的输入!")
        sys.exit(1)

    # 获取绝对路径并验证
    selected_files = modes[choice]["files"]
    processes = []
    
    for rel_path in selected_files:
        abs_path = os.path.join(root_path, rel_path)
        if not os.path.exists(abs_path):
            print(f"错误：文件 {abs_path} 不存在")
            sys.exit(1)

        # 启动子进程
        p = subprocess.Popen([sys.executable, abs_path])
        processes.append(p)
        print(f"已启动: {rel_path} (PID: {p.pid})")

    # 信号处理函数
    def signal_handler(sig, frame):
        print("\n收到终止信号，正在停止所有进程...")
        for p in processes:
            if p.poll() is None:  # 检查是否仍在运行
                p.terminate()
                try:
                    p.wait(timeout=3)
                    print(f"进程 {p.pid} 已终止")
                except subprocess.TimeoutExpired:
                    p.kill()
                    print(f"强制终止进程 {p.pid}")
        sys.exit(0)

    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)

    # 主进程保持运行
    try:
        while any(p.poll() is None for p in processes):
            time.sleep(1)
        print("所有进程已正常退出")
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)

if __name__ == "__main__":
    main()