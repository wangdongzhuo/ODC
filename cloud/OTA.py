import requests

# Flask 应用的 URL
#base_url = 'http://127.0.0.1:5001' #ODC接口
base_url = 'http://127.0.0.1:5002' #天气接口
# 访问 /get_data 接口
response = requests.get(f'{base_url}/get_data')

# 检查请求是否成功
if response.status_code == 200:
    # 打印返回的 JSON 数据
    print(response.json())
else:
    print(f'请求失败，状态码：{response.status_code}')



