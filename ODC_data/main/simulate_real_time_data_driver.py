import time
import os
import random

def get_root_path():
    """
    获取ODCSOFT_KINGLONG的根路径
    """
    current_path = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件的绝对路径
    root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))  # 向上回溯三层到根目录
    return root_path
print(os.path.join(get_root_path(), "monitorODC\\ODC_data\\data-original\\driver_state_messages.txt"))
class DriverStateSimulator:
    """驾驶员状态数据模拟器"""

    def __init__(self):
        # 使用相对路径构建完整路径
        root_path = get_root_path()
        self.source_file = os.path.join(root_path, "monitorODC\\ODC_data\\data-original\\driver_state_messages.txt")
        self.target_file = os.path.join(root_path, "monitorODC\\ODC_data\\data-real-time\\driver_state_messages.txt")

    def ensure_target_dir_exists(self):
        """确保目标目录存在"""
        target_dir = os.path.dirname(self.target_file)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            print(f"[信息] 创建目录: {target_dir}")

    def load_source_data(self):
        """加载源数据文件"""
        try:
            if not os.path.exists(self.source_file):
                print(f"[错误] 源文件不存在: {self.source_file}")
                return []

            # 添加 encoding 参数，根据文件实际编码选择
            with open(self.source_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 过滤掉注释行和空行
            valid_lines = [line.strip() for line in lines
                           if line.strip() and not line.strip().startswith('#')]
            return valid_lines
        except Exception as e:
            print(f"[错误] 加载源文件失败: {str(e)}")
            return []

    def simulate_real_time_data(self):
        """模拟实时数据写入"""
        print("[信息] 开始模拟驾驶员状态数据...")
        self.ensure_target_dir_exists()

        source_data = self.load_source_data()
        if not source_data:
            print("[错误] 无可用的源数据")
            return

        # print("[信息] 开始模拟实时数据写入...")

        try:
            while True:
                # 随机选择一条数据
                line = random.choice(source_data)

                # 更新时间戳为当前时间
                parts = line.split()
                current_time = int(time.time())
                updated_line = f"{current_time} {' '.join(parts[1:])}"

                # 写入目标文件
                with open(self.target_file, 'w', encoding='utf-8') as f:
                    f.write(updated_line)

                # 输出状态信息
                # print(f"\n[信息] 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                # print(f"写入数据: {updated_line}")

                time.sleep(0.2)  # 每2秒更新一次

        except KeyboardInterrupt:
            print("\n[信息] 模拟器已停止")
        except Exception as e:
            print(f"[错误] 模拟过程发生异常: {str(e)}")


def main():
    """主函数"""
    print("[信息] 启动驾驶员状态数据模拟器...")
    simulator = DriverStateSimulator()
    simulator.simulate_real_time_data()


if __name__ == "__main__":
    main()
