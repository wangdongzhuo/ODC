import requests
import time
import os
from datetime import datetime  # 新增datetime模块

def get_root_path():
    """
    获取ODCSOFT_KINGLONG的根路径
    """
    current_path = os.path.dirname(os.path.abspath(__file__))  # 获取当前文件的绝对路径
    root_path = os.path.dirname(os.path.dirname(current_path))  # 向上回溯三层到根目录
    return root_path

def send_2_cloud_save():
    root_path = get_root_path()
    aim_dir_path = os.path.join(root_path, "monitorODC\\send2cloud")
    file_path = os.path.join(aim_dir_path, "lasted.json")

    while True:
        if os.path.isfile(file_path):
            if signal == 1:
                # 生成带时间戳的新文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # 格式：年月日_时分秒
                original_name = "lasted.json"
                base_name, ext = os.path.splitext(original_name)
                new_filename = f"{base_name}_{timestamp}{ext}"  # 例如 lasted_20231015_1430.json

                server_url = "http://8.152.217.194:5008/upload"

                with open(file_path, "rb") as file:
                    # 使用新文件名作为上传文件名
                    files = {"file": (new_filename, file)}
                    response = requests.post(server_url, files=files)

                print(f"上传 {new_filename} 的响应:", response.text)
            else:
                print("已完成一次上传")
            os.remove(file_path)

        time.sleep(0.1)


if __name__ == '__main__':
    signal = 0  # 0为不上传测试，1为上传
    send_2_cloud_save()
