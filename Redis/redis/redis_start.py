import redis
import time
import subprocess
import socket

# 启动 Redis 服务器（使用指定的配置文件）
def start_redis():
    try:
        # 启动 Redis 服务器
        subprocess.Popen([r"Redis\ProgramFile\Redis\redis-server.exe"])  # 不使用指定的配置文件
        print("Redis 服务器已启动")
    except Exception as e:
        print("启动 Redis 服务器时出错:", e)

# 检查 Redis 是否启动成功
def check_redis_running():
    try:
        # 尝试连接 Redis 服务器（默认端口 6379）
        r = redis.Redis(host='localhost', port=6379)
        r.ping()  # 尝试发送 PING 请求
        print("Redis 已成功连接")
        return True
    except redis.ConnectionError:
        print("无法连接到 Redis 服务器，等待重试...")
        return False

# 启动 Redis 服务器
start_redis()

# 等待 Redis 启动完成并检查连接
max_retries = 10  # 最大重试次数
for _ in range(max_retries):
    if check_redis_running():
        break
    time.sleep(2)  # 等待 2 秒后重试
else:
    print("Redis 启动失败，超出了最大重试次数")
