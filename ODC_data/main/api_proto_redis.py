import os
import subprocess
import time
import redis
import sys
import atexit
import pickle

# 多个proto文件路径配置
PROTO_FILE_PATHS = [
    r"C:\Users\wdz\Desktop\ODCmonitor\ODCmonitor\monitorODC\Redis\redis\test_data\lanelist.proto",
    r"C:\Users\wdz\Desktop\ODCmonitor\ODCmonitor\monitorODC\Redis\redis\test_data\mmobstacles.proto",
    r"C:\Users\wdz\Desktop\ODCmonitor\ODCmonitor\monitorODC\Redis\redis\test_data\location.proto",
    r"C:\Users\wdz\Desktop\ODCmonitor\ODCmonitor\monitorODC\Redis\redis\test_data\trafficlightlist.proto"
]

REDIS_EXE_PATH = r"C:\Users\wdz\Desktop\ODCmonitor\ODCmonitor\monitorODC\Redis\ProgramFile\Redis\redis-server.exe"

# Redis配置
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# 全局变量
redis_process = None
redis_client = None

def start_redis():
    """启动Redis服务"""
    global redis_process
    if not os.path.exists(REDIS_EXE_PATH):
        print(f"[错误] Redis可执行文件不存在: {REDIS_EXE_PATH}")
        return False

    try:
        redis_process = subprocess.Popen(
            [REDIS_EXE_PATH],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        print(f"[信息] Redis服务启动，进程ID: {redis_process.pid}")
        time.sleep(2)
        return True
    except Exception as e:
        print(f"[错误] 启动Redis失败: {str(e)}")
        return False

def init_redis_client():
    """初始化Redis客户端"""
    global redis_client
    try:
        redis_client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=False
        )
        redis_client.ping()
        print("[信息] Redis客户端连接成功")
        return True
    except Exception as e:
        print(f"[错误] Redis连接失败: {str(e)}")
        return False

def read_and_serialize_proto(file_path):
    """读取并序列化单个proto文件"""
    if not os.path.exists(file_path):
        print(f"[错误] proto文件不存在: {file_path}")
        return None, None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            proto_text = f.read()
        
        # 基于文件名生成Redis键
        filename = os.path.basename(file_path)
        redis_key = f"proto_{os.path.splitext(filename)[0]}"
        serialized_data = pickle.dumps(proto_text)
        print(f"[信息] 已处理 {filename}，键: {redis_key}")
        return redis_key, serialized_data
    except Exception as e:
        print(f"[错误] 处理文件 {file_path} 失败: {str(e)}")
        return None, None

def save_to_redis(redis_key, serialized_data):
    """存储数据到Redis"""
    if not redis_client or not redis_key or not serialized_data:
        return False

    try:
        redis_client.set(redis_key, serialized_data)
        return True
    except Exception as e:
        print(f"[错误] 存储键 {redis_key} 失败: {str(e)}")
        return False

def cleanup():
    """程序退出时关闭Redis服务"""
    global redis_process
    if redis_process:
        try:
            redis_process.terminate()
            time.sleep(1)
            print(f"[信息] Redis服务已关闭，进程ID: {redis_process.pid}")
        except Exception as e:
            print(f"[错误] 关闭Redis失败: {str(e)}")

atexit.register(cleanup)

def keep_running():
    """保持程序运行"""
    try:
        print("\n===== 所有文件处理完成 =====")
        print("Redis服务运行中，按Ctrl+C停止")
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        print("\n[信息] 用户中断程序")

if __name__ == '__main__':
    print("===== 启动多proto文件写入服务 =====")
    
    if not start_redis():
        sys.exit(1)
    
    if not init_redis_client():
        cleanup()
        sys.exit(1)
    
    all_success = True
    for path in PROTO_FILE_PATHS:
        key, data = read_and_serialize_proto(path)
        if key and data and not save_to_redis(key, data):
            all_success = False
        elif not key or not data:
            all_success = False
    
    if not all_success:
        print("\n[警告] 部分文件处理失败")
    
    keep_running()
