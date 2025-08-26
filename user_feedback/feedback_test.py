# # 1. HTML修改
# <!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>反馈表单</title>
# </head>
# <body>
#     <h1>反馈表单</h1>
#     <form id="feedbackForm">
#         <label for="content">反馈内容：</label><br>
#         <textarea id="content" name="content" rows="4" cols="50" required></textarea><br><br>

#         <label for="contact">联系方式（可选）：</label><br>
#         <input type="text" id="contact" name="contact"><br><br>

#         <label for="deviceInfo">设备信息（可选）：</label><br>
#         <input type="text" id="deviceInfo" name="deviceInfo"><br><br>

#         <label for="location">位置信息：</label><br>
#         <input type="text" id="location" name="location" required><br><br>

#         <button type="submit">提交反馈</button>
#     </form>

#     <script>
#         document.getElementById('feedbackForm').addEventListener('submit', async (e) => {
#             e.preventDefault();

#             const content = document.getElementById('content').value;
#             const contact = document.getElementById('contact').value;
#             const deviceInfo = document.getElementById('deviceInfo').value;
#             const location = document.getElementById('location').value;

#             const payload = {
#                 content,
#                 contact,
#                 deviceInfo,
#                 location
#             };

#             try {
#                 const response = await fetch('http://localhost:5009/nav_feedback/submit', {
#                     method: 'POST',
#                     headers: {
#                         'Content-Type': 'application/json'
#                     },
#                     body: JSON.stringify(payload)
#                 });

#                 const result = await response.json();
#                 if (response.status === 201) {
#                     alert('反馈提交成功！');
#                 } else {
#                     alert(`反馈提交失败：${result.message}`);
#                 }
#             } catch (error) {
#                 console.error('提交反馈时出错:', error);
#                 alert('反馈提交失败，请稍后再试。');
#             }
#         });
#     </script>
# </body>
# </html>


import requests

def get_user_input():
    content = input("请输入反馈内容：")
    contact = input("请输入联系方式（可选）：")
    device_info = input("请输入设备信息（可选）：")
    location = input("请输入位置信息：")
    
    return {
        "content": content,
        "contact": contact,
        "deviceInfo": device_info,
        "location": location
    }

def submit_feedback(payload):
    url = "http://localhost:5009/nav_feedback/submit"
    response = requests.post(url, json=payload)
    result = response.json()
    
    if response.status_code == 201:
        print("反馈提交成功！")
    else:
        print(f"反馈提交失败：{result.get('message', '未知错误')}")

if __name__ == "__main__":
    payload = get_user_input()
    submit_feedback(payload)