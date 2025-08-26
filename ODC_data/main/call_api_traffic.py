import requests
import random
api_dict=['c4f1e88fb7df0edf52c0b0fc9a84dec1','28f0e1d0ace50da26f501fec59a2e705','f6cc8ee9198302b6071ed9b248ffae2f','261c38756bcf209c2a94e34f5bc26639','1d94f7a1fbdd891a3f3d898682ef6c41','8e4a412af7d7be006de8c87eb0623ffc','607271b9d28a964762368b1ecaee992c','98367b490da8ab61c591328815d70716']

def get_traffic_status(center_lat, center_lng, radius=100):
    """
    查询圆形区域内的交通拥堵信息和交通事件信息
    :param center_lat: 圆心纬度
    :param center_lng: 圆心经度
    :param radius: 圆形区域半径（单位：米）
    :param api_key: 高德API Key
    :return: 查询结果
    """
    url = "https://restapi.amap.com/v3/traffic/status/circle"
    index=random.randint(0,len(api_dict)-1)
    params = {
        "key": api_dict[index],
        "location": f"{center_lng},{center_lat}",  # 经度在前，纬度在后
        "radius": radius,
        "extensions": "base"  # 返回完整信息，包括交通事件
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "1":
            return data
        else:
            print(f"Error: {data['info']}")
            return None
    else:
        print(f"HTTP Error: {response.status_code}")
        return None

# 示例调用
if __name__ == "__main__":
    center_latitude = 39.98641364  # 圆心纬度
    center_longitude =  116.3057764  # 圆心经度
    result = get_traffic_status(center_latitude, center_longitude)
    print(result)