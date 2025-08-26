import requests
import time
import json
from flask import Flask, jsonify
# 接口URL
url = "https://api.caiyunapp.com/v2.6/5dkE64l8KOHrjY4s/106.3613,29.5569/realtime"
# 调用接口的函数
app = Flask(__name__)
def call_api():
    response = requests.get(url)
    if response.status_code == 200:
        data_raw=response.json()
        data = data_raw['result']['realtime']
        extracted_data = {
            "时间帧": data_raw["server_time"],
            "气温": data["temperature"],#摄氏度
            "湿度": data["humidity"], #0-1
            "多云率": data["cloudrate"], #多云率
            "天气": data["skycon"],
            "能见度": data["visibility"]*1000, #m
            "风速": data["wind"]["speed"], #km/h
            "风向": data["wind"]["direction"], #从北顺时针
            "本地降水量": data["precipitation"]["local"]["intensity"],#雷达降水强度【0.031 无雨雪,0.25 小雨/雪,0.35 中雨/雪，0.48 大雨雪，1 暴雨雪】
            "AQI值": data["air_quality"]["aqi"]["chn"] #国标 AQI
        }
        formatted_data=json.dumps(extracted_data,indent=4,ensure_ascii=False )
        print(formatted_data)
        return extracted_data
    else:
        print("Failed to retrieve data:", response.status_code)

# 设置调用频率，例如每10秒调用一次
integal = 60
json_data = call_api()
time_begin = int(time.time()/integal)

@app.route('/get_data', methods=['GET'])
def get_data():
    # 返回JSON响应
    global json_data, time_begin
    current_time=int(time.time()/integal)
    if current_time!=time_begin:
        json_data=call_api()
        time_begin=current_time
    else:
        pass
    return jsonify(json_data)


if __name__ == '__main__':
    app.run(host='127.0.0.1',port=5005,debug=True)

