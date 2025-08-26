from flask import Flask, jsonify
import os
import time

app = Flask(__name__)

# 获取当前文件的绝对路径
def get_root_path():
    """
    获取ODCSOFT_KINGLONG的根路径
    """
    current_path = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件的绝对路径
    root_path = os.path.dirname(os.path.dirname(os.path.dirname(current_path)))  # 向上回溯三层到根目录
    return root_path
# 使用相对路径构建完整路径
root_path = get_root_path()
file_path = os.path.join(root_path, "monitorODC\\ODC_data\\data-real-time\\driver_state_messages.txt")

class DriverStateParser:
    """驾驶员状态数据解析器"""
    
    def __init__(self, file_path):
        self.file_path = file_path
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
            0x0c: "偏离遮阳镜"
        }
        
    def parse_frame(self, frame_str):
        """解析帧数据"""
        parts = frame_str.strip().split()
        if len(parts) < 7:  # 时间戳 + 6个帧字段
            return None
            
        timestamp = int(parts[0])
        frame_data = parts[1:]  # 剩余部分是帧数据
        
        # 提取状态码
        state_code = int(frame_data[3], 16)  # 第4个字段是数据位
        
        # 构建帧字典
        frame = {
            'head': frame_data[0],
            'cmd': frame_data[1],
            'length': frame_data[2],
            'data': frame_data[3],
            'check': frame_data[4],
            'tail': frame_data[5]
        }
        
        # 构建完整响应
        response = {
            'timestamp': timestamp,
            'frame': frame,
            'raw_frame': ' '.join(frame_data),
            'state_code': f'0x{state_code:02X}',
            'state_description': self.state_codes.get(state_code, "未知状态")
        }
        
        return response
        
    def get_current_state(self):
        """获取当前状态"""
        try:
            if not os.path.exists(self.file_path):
                return None
                
            current_time = int(time.time())
            
            with open(self.file_path, 'r') as f:
                lines = f.readlines()
                
            # 跳过注释行
            valid_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
            
            # 找到最接近当前时间的数据
            closest_line = None
            min_diff = float('inf')
            
            for line in valid_lines:
                try:
                    timestamp = int(line.split()[0])
                    diff = abs(current_time - timestamp)
                    if diff < min_diff:
                        min_diff = diff
                        closest_line = line
                except (ValueError, IndexError):
                    continue
            
            if closest_line:
                return self.parse_frame(closest_line)
            return None
            
        except Exception as e:
            print(f"[错误] 读取状态数据失败: {str(e)}")
            return None

# 创建解析器实例
parser = DriverStateParser(file_path)

@app.route('/get_driver_state', methods=['GET'])
def get_driver_state():
    """获取驾驶员状态数据"""
    try:
        state_data = parser.get_current_state()
        print(state_data)
        if state_data is None:
            return jsonify({"错误信息": "无法获取状态数据"}), 404
        return jsonify(state_data), 200
    except Exception as e:
        error_msg = f"获取驾驶员状态失败: {str(e)}"
        print(f"[错误] {error_msg}")
        return jsonify({"错误信息": error_msg}), 500

if __name__ == '__main__':
    print("[信息] 启动驾驶员状态监测 API 服务")
    print(f"[信息] 使用数据文件: {file_path}")
    if not os.path.exists(file_path):
        print(f"[警告] 数据文件不存在: {file_path}")
    app.run(host='127.0.0.1', port=5003, debug=True) 