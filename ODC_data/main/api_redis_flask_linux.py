from flask import Flask, jsonify, request
import redis
import pickle
import time

app = Flask(__name__)
app.json.ensure_ascii = False

# Redis配置
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

redis_client = None

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
        
        # 连接重试机制
        retries = 5
        while retries > 0:
            try:
                redis_client.ping()
                print("[信息] Redis客户端连接成功")
                return True
            except:
                retries -= 1
                print(f"[警告] Redis连接失败，剩余重试次数: {retries}")
                time.sleep(2)
        
        print("[错误] 无法连接到Redis服务")
        return False
        
    except Exception as e:
        print(f"[错误] Redis连接失败: {str(e)}")
        return False

def load_proto_data(redis_key):
    """从Redis读取并反序列化数据"""
    if not redis_client:
        return None

    try:
        serialized_data = redis_client.get(redis_key)
        if not serialized_data:
            return None
        
        return pickle.loads(serialized_data)
    except Exception as e:
        print(f"[错误] 处理键 {redis_key} 失败: {str(e)}")
        return None

@app.route('/get_protobuf', methods=['GET'])
def get_protobuf():
    """获取指定proto文件内容（通用接口）"""
    filename = request.args.get('filename')
    if not filename:
        return jsonify({"错误": "请提供filename参数"}), 400
    
    redis_key = f"proto_{filename}"
    content = load_proto_data(redis_key)
    
    if content:
        return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    return jsonify({"错误": f"未找到 {filename}.proto"}), 404

# 为每个特定文件创建单独的路由
@app.route('/get_lanelist', methods=['GET'])
def get_lanelist():
    """获取lanelist proto文件内容"""
    redis_key = "proto_lanelist"
    content = load_proto_data(redis_key)
    
    if content:
        return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    return jsonify({"错误": "未找到lanelist.proto"}), 404

@app.route('/get_trafficlightlist', methods=['GET'])
def get_trafficlightlist():
    """获取trafficlightlist proto文件内容"""
    redis_key = "proto_trafficlightlist"
    content = load_proto_data(redis_key)
    
    if content:
        return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    return jsonify({"错误": "未找到trafficlightlist.proto"}), 404

@app.route('/get_location', methods=['GET'])
def get_location():
    """获取location proto文件内容"""
    redis_key = "proto_location"
    content = load_proto_data(redis_key)
    
    if content:
        return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    return jsonify({"错误": "未找到location.proto"}), 404

@app.route('/get_mmobstacles', methods=['GET'])
def get_mmobstacles():
    """获取mmobstacles proto文件内容"""
    redis_key = "proto_mmobstacles"
    content = load_proto_data(redis_key)
    
    if content:
        return content, 200, {'Content-Type': 'text/plain; charset=utf-8'}
    return jsonify({"错误": "未找到mmobstacles.proto"}), 404

@app.route('/list_protobufs', methods=['GET'])
def list_protobufs():
    """列出所有可用的proto文件"""
    if not redis_client:
        return jsonify({"错误": "Redis连接未初始化"}), 500
    
    try:
        keys = redis_client.keys("proto_*")
        filenames = [key.decode().replace("proto_", "") for key in keys]
        return jsonify({"可用文件": filenames}), 200
    except Exception as e:
        print(f"[错误] 列出文件失败: {str(e)}")
        return jsonify({"错误": "获取文件列表失败"}), 500

if __name__ == '__main__':
    print("===== 启动多proto文件读取服务 =====")
    
    if not init_redis_client():
        exit(1)
    
    print("\n===== 服务启动完成 =====")
    print(f"获取trafficlightlist文件: http://127.0.0.1:5004/get_trafficlightlist")
    print(f"获取lanelist文件: http://127.0.0.1:5004/get_lanelist")
    print(f"获取location文件: http://127.0.0.1:5004/get_location")
    print(f"获取mmobstacles文件: http://127.0.0.1:5004/get_mmobstacles")

    app.run(host='127.0.0.1', port=5004, debug=True, use_reloader=False)
