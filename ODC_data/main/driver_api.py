import serial
from flask import Flask, jsonify
import time
import threading
import atexit  # 用于确保程序退出时关闭串口

app = Flask(__name__)

# 串口配置
SERIAL_PORT = 'COM4'  # 使用你实际的串口号
BAUDRATE = 9600
TIMEOUT = 1
ser = None  # 串口对象，全局使用

class DriverStateParser:
    """驾驶员状态数据解析器"""

    def __init__(self):
        self.state_codes = {
            0x00: "无报警",
            0x01: "抽烟",
            0x02: "打电话",
            0x03: "闭眼",
            0x04: "低头",
            0x05: "转头",
            0x06: "打盹",
            0x07: "喝水",
            0x08: "打哈欠",
            0x09: "遮挡摄像头",
            0x0a: "检测不到人脸",
            0x0b: "未系安全带",
            0x0c: "佩戴遮阳镜"
        }
        self.latest_state = None  # 存储最新的解析结果

    def parse_frame(self, frame_data):
        """解析串口接收的帧数据"""
        # 查找连续的 '7E C5 01' 并提取后续数据
        for i in range(len(frame_data) - 2):
            if frame_data[i] == '7E' and frame_data[i+1] == 'C5' and frame_data[i+2] == '01':
                # 获取状态码
                state_code = int(frame_data[i+3], 16)  # 假设状态码在 '7E C5 01' 后面的第一个字节
                # 返回对应状态描述
                state_description = self.state_codes.get(state_code, "未知状态")
                self.latest_state = {
                    'state_code': f'0x{state_code:02X}',
                    'state_description': state_description
                }
                return self.latest_state
        return None  # 如果没有找到有效的 '7E C5 01'，返回 None


# 创建解析器实例
parser = DriverStateParser()

def open_serial_port():
    """尝试打开串口"""
    global ser
    try:
        print(f"[信息] 尝试打开串口 {SERIAL_PORT}...")
        ser = serial.Serial(SERIAL_PORT, baudrate=BAUDRATE, timeout=TIMEOUT)
        print(f"[信息] 串口 {SERIAL_PORT} 已打开")
    except serial.SerialException as e:
        print(f"[错误] 无法打开串口 {SERIAL_PORT}：{e}")
        ser = None

def read_serial_data():
    """后台线程：实时读取串口数据"""
    global ser
    incomplete_data = []  # 用于存储跨行的数据

    if ser:
        try:
            while True:  # 持续不断地读取串口数据
                data = ser.readline()
                if data:
                    hex_data = ' '.join(f'{b:02X}' for b in data)
                    frame_data = hex_data.split()

                    # 尝试解析数据
                    result = parser.parse_frame(frame_data)
                    if result:
                        print(f"[信息] 最新驾驶员状态: {result['state_description']}")

        except Exception as e:
            print(f"[错误] 串口读取失败: {str(e)}")
        finally:
            if ser and ser.is_open:
                ser.close()  # 确保退出时关闭串口


@app.route('/get_driver_state', methods=['GET'])
def get_driver_state():
    """返回最新的驾驶员状态"""
    if parser.latest_state:
        return jsonify(parser.latest_state), 200
    else:
        return jsonify({"错误信息": "暂无数据"}), 404


def close_serial_port():
    """确保程序退出时关闭串口"""
    if ser and ser.is_open:
        ser.close()
        print("[信息] 串口已关闭")


if __name__ == '__main__':
    print("[信息] 启动驾驶员状态监测 API 服务")

    # 确保程序退出时串口被关闭
    atexit.register(close_serial_port)

    # 启动串口打开操作
    open_serial_port()

    if ser is None:
        print("[错误] 无法打开串口，程序无法继续运行。")
    else:
        # 启动串口读取线程
        serial_thread = threading.Thread(target=read_serial_data, daemon=True)
        serial_thread.start()

        # 启动 Flask 服务（禁用自动重启）
        app.run(host='0.0.0.0', port=5003, debug=False)  # debug=False 禁用自动重启
