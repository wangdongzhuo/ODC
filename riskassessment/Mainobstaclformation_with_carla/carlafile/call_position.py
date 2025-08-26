import requests
import time

def get_risk_data():
    url = "http://127.0.0.1:5012/get_position_data"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "message" in data:
                print("暂无数据：", data["message"])
            else:
                print(f"检测到风险车辆：")
                print(f"车辆ID: {data['vehicle_id']}")
                print(f"TTC值: {data['TTC']}")
                print(f"风险值: {data['risk_field']}")
                print(f"相对位置: x={data['posx']:.2f}, y={data['posy']:.2f}")
                print(f"相对速度: vx={data['relvelx']:.2f}, vy={data['relvely']:.2f}")
                print("-" * 50)
    except requests.exceptions.ConnectionError:
        print("无法连接到服务器，请确保模拟器正在运行")

def main():
    print("开始监控风险数据...")
    try:
        while True:
            get_risk_data()
            time.sleep(1)  # 每秒更新一次数据
    except KeyboardInterrupt:
        print("\n程序已停止")

if __name__ == "__main__":
    main()