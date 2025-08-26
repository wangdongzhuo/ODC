from flask import Flask, request, jsonify
import datetime
import uuid

app = Flask(__name__)

# 模拟存储反馈数据的字典
feedbacks = {}

@app.route('/nav_feedback/submit', methods=['POST'])
def submit_feedback():
    # 解析请求数据
    data = request.get_json()
    content = data.get('content')
    contact = data.get('contact')
    device_info = data.get('deviceInfo', {})
    location = data.get('location')
    screenshot = data.get('screenshot')

    # 验证必要字段
    if not content:
        return jsonify({"status": "error", "message": "反馈内容不能为空！"}), 400

    if not location:
        return jsonify({"status": "error", "message": "位置信息不能为空！"}), 400

    # 生成唯一ID
    feedback_id = str(uuid.uuid4())

    # 保存反馈数据
    feedbacks[feedback_id] = {
        "id": feedback_id,
        "content": content,
        "contact": contact,
        "deviceInfo": device_info,
        "location": location,
        "screenshot": screenshot,
        "createdAt": datetime.datetime.now().isoformat(),
        "status": "未处理"
    }

    return jsonify({
        "status": "success",
        "message": "反馈已提交，感谢您的支持！"
    }), 201

@app.route('/nav_feedback/list', methods=['GET'])
def get_feedback_list():
    page = int(request.args.get('page', 1))
    page_size = int(request.args.get('pageSize', 10))
    start = (page - 1) * page_size
    end = start + page_size

    feedback_list = list(feedbacks.values())
    total = len(feedback_list)

    # 分页
    paginated_data = feedback_list[start:end]

    return jsonify({
        "page": page,
        "pageSize": page_size,
        "total": total,
        "data": paginated_data
    })

@app.route('/nav_feedback/<string:feedback_id>', methods=['GET'])
def get_feedback(feedback_id):
    feedback = feedbacks.get(feedback_id)
    if not feedback:
        return jsonify({"status": "error", "message": "反馈不存在！"}), 404
    return jsonify(feedback)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5009, debug=True) 