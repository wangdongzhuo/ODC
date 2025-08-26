import time
import os

def get_root_path():
    """
    获取ODCSOFT_KINGLONG的根路径
    """
    current_path = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件的绝对路径
    root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))  # 向上回溯三层到根目录
    return root_path
# 使用相对路径构建完整路径
root_path = get_root_path()
source_file = os.path.join(root_path, "monitorODC\\ODC_data\\data-original\\2025-03-05_15点53分_单ACC_20KM跟车距离远.txt")
# 输出文件（实时更新的目标文件）
target_file = os.path.join(root_path, "monitorODC\\ODC_data\\data-real-time\\香港车ECAN.txt")

def ensure_target_file_exists():
    """检查目标文件是否存在，如果不存在则创建"""
    if not os.path.exists(target_file):
        with open(target_file, "w") as file:
            # 写入初始化内容（例如元信息）
            file.write("// Real-time simulated CAN data\n")
            file.write("base hex  timestamps absolute\n")
            print(f"Created new file: {target_file}")

def simulate_real_time_data():
    """根据原时间戳间隔实时写入目标文件"""
    with open(source_file, "r") as src, open(target_file, "w") as tgt:
        previous_timestamp = None  # 保存上一条记录的时间戳
        simulation_start_time = time.time()  # 模拟开始的时间点

        for line in src:
            # 跳过非数据行
            if not line.strip() or line.startswith("//") or line.startswith("base") or line.startswith("Begin") or "Start of measurement" in line or line.startswith("date"):
                tgt.write(line)
                tgt.flush()
                continue

            # 提取当前行的时间戳
            parts = line.strip().split()
            if len(parts) < 5:
                continue  # 跳过格式不完整的行

            try:
                current_timestamp = float(parts[0])  # 提取当前行的时间戳
            except ValueError:
                continue  # 跳过无效时间戳

            # 计算时间间隔，并模拟真实写入的时间
            if previous_timestamp is not None:
                time_interval = current_timestamp - previous_timestamp
                if time_interval > 0:
                    time.sleep(time_interval)  # 等待指定的时间间隔

            # 写入目标文件
            tgt.write(line)
            tgt.flush()  # 确保数据立即写入文件
            # print(f"Written: {line.strip()}")  # 打印写入内容，用于调试

            # 更新上一条时间戳
            previous_timestamp = current_timestamp

if __name__ == "__main__":
    print("Starting to simulate real-time data...")
    simulate_real_time_data()
    print("Simulation completed.")
