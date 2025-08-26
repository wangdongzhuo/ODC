import platform
from ctypes import *
import threading
import time
from flask import Flask, jsonify
from parsers.rules_mapping import get_parser
import os
import json

# ---------------- USB CAN 部分开始 -------------------
lib = cdll.LoadLibrary("./libusbcan.so")

USBCAN_I = c_uint32(3)  # USBCAN-I/I+ 3
USBCAN_II = c_uint32(4)  # USBCAN-II/II+ 4
MAX_CHANNELS = 2  # 通道最大数量
g_thd_run = 1  # 线程运行标志


class ZCAN_CAN_BOARD_INFO(Structure):
    _fields_ = [("hw_Version", c_ushort),
                ("fw_Version", c_ushort),
                ("dr_Version", c_ushort),
                ("in_Version", c_ushort),
                ("irq_Num", c_ushort),
                ("can_Num", c_ubyte),
                ("str_Serial_Num", c_ubyte * 20),
                ("str_hw_Type", c_ubyte * 40),
                ("Reserved", c_ubyte * 4)]

    def __str__(self):
        return "Hardware Version:%s\nFirmware Version:%s\nDriver Version:%s\nInterface:%s\nInterrupt Number:%s\nCAN_number:%d" % (
            self.hw_Version, self.fw_Version, self.dr_Version, self.in_Version, self.irq_Num, self.can_Num)

    def serial(self):
        serial = ''
        for c in self.str_Serial_Num:
            if c > 0:
                serial += chr(c)
            else:
                break
        return serial

    def hw_Type(self):
        hw_Type = ''
        for c in self.str_hw_Type:
            if c > 0:
                hw_Type += chr(c)
            else:
                break
        return hw_Type


class ZCAN_CAN_INIT_CONFIG(Structure):
    _fields_ = [("AccCode", c_int),
                ("AccMask", c_int),
                ("Reserved", c_int),
                ("Filter", c_ubyte),
                ("Timing0", c_ubyte),
                ("Timing1", c_ubyte),
                ("Mode", c_ubyte)]


class ZCAN_CAN_OBJ(Structure):
    _fields_ = [("ID", c_uint32),
                ("TimeStamp", c_uint32),
                ("TimeFlag", c_uint8),
                ("SendType", c_byte),
                ("RemoteFlag", c_byte),
                ("ExternFlag", c_byte),
                ("DataLen", c_byte),
                ("Data", c_ubyte * 8),
                ("Reserved", c_ubyte * 3)]


def GetDeviceInf(DeviceType, DeviceIndex):
    try:
        info = ZCAN_CAN_BOARD_INFO()
        ret = lib.VCI_ReadBoardInfo(DeviceType, DeviceIndex, byref(info))
        return info if ret == 1 else None
    except Exception as e:
        print("Exception on readboardinfo:", e)
        raise


# 全局CAN数据缓冲区，用于存储接收到的CAN数据行
can_buffer = []
can_buffer_lock = threading.Lock()


def usb_can_rx_thread(DeviceType, DevIdx, chn_idx):
    """
    接收 USB CAN 数据，将每条CAN帧格式化为新格式字符串后写入全局缓冲区
    新格式示例：
      [15572710] 0 ID: 0x18FF70C8 扩展帧 Data: 00 00 00 00 00 00 00 70
    """
    global g_thd_run, can_buffer
    while g_thd_run == 1:
        time.sleep(0.1)
        count = lib.VCI_GetReceiveNum(DeviceType, DevIdx, chn_idx)
        if count > 0:
            can_array = (ZCAN_CAN_OBJ * count)()
            rcount = lib.VCI_Receive(DeviceType, DevIdx, chn_idx, byref(can_array), count, 100)
            for i in range(rcount):
                can_obj = can_array[i]
                # 使用当前时间戳（整数形式）作为时间戳，并加上中括号
                timestamp = int(time.time())
                can_id = f"0x{can_obj.ID:08X}"
                # 将数据字节转换为两位16进制字符串（按DataLen有效字节）
                raw_data = " ".join(f"{can_obj.Data[j]:02x}" for j in range(can_obj.DataLen))
                # 判断帧类型
                frame_type = "扩展帧" if can_obj.ExternFlag == 1 else "标准帧"
                # 构造新的数据格式
                line = f"[{timestamp}] {chn_idx} ID: {can_id} {frame_type} raw_data: {raw_data}"
                with can_buffer_lock:
                    can_buffer.append(line)


# ---------------- USB CAN 部分结束 -------------------

app = Flask(__name__)

# 修改后的初始化数据字典（保持原有解析逻辑不变）
all_categories = {
    "控制转向系统报文": {"timestamp": 0, "data": {}},
    "控制驱动和制动系统报文": {"timestamp": 0, "data": {}},
    "状态反馈和状态请求报文": {"timestamp": 0, "data": {}},
    "状态反馈和状态请求报文2": {"timestamp": 0, "data": {}},
    "协同控制器系统故障报文": {"timestamp": 0, "data": {}},
    "AS控制L2系统报文": {"timestamp": 0, "data": {}},
    "驱动状态报文": {"timestamp": 0, "data": {}},
    "域控制器基础信息1": {"timestamp": 0, "data": {}},
    "域控制器基础信息2": {"timestamp": 0, "data": {}},
    "高压电池状态报文": {"timestamp": 0, "data": {}},
    "域控制器基础信息": {"timestamp": 0, "data": {}},
    "转向系统状态反馈": {"timestamp": 0, "data": {}},
    "L2功能状态反馈": {"timestamp": 0, "data": {}},
    "智能控制状态反馈": {"timestamp": 0, "data": {}},
    "智能车辆状态反馈": {"timestamp": 0, "data": {}},
    "车辆车速报文": {"timestamp": 0, "data": {}},
    "轮速报文": {"timestamp": 0, "data": {}},
    "胎压监控系统状态": {"timestamp": 0, "data": {}},
    "车辆加速度信息": {"timestamp": 0, "data": {}},
    "主目标信息": {"timestamp": 0, "data": {}},
    "车辆里程总报文": {"timestamp": 0, "data": {}},
    "左车道线状态1": {"timestamp": 0, "data": {}},
    "左车道线状态2": {"timestamp": 0, "data": {}},
    "右车道线状态1": {"timestamp": 0, "data": {}},
    "右车道线状态2": {"timestamp": 0, "data": {}}
}

no_data_logged = False  # 控制日志输出的全局标志位


def read_new_can_lines():
    """
    从全局缓冲区中读取新增的CAN数据行并解析（基于新的数据格式）
    格式示例：
      [15572710] 0 ID: 0x18FF70C8 扩展帧 Data: 00 00 00 00 00 00 00 70
    :return: 包含解析结果的完整字典
    """
    global can_buffer, all_categories
    # 每隔0.05秒检查一次是否有新数据，最长等待1秒
    wait_time = 0
    while True:
        with can_buffer_lock:
            if can_buffer:
                break
        time.sleep(0.05)
        wait_time += 0.05
        if wait_time >= 1.0:
            print("[Info] No new CAN lines found.")
            return all_categories

    # 读取并清空缓冲区
    with can_buffer_lock:
        lines = can_buffer[:]
        can_buffer.clear()
    print(f"[Debug] Read {len(lines)} new CAN lines from buffer.")

    # 按新格式解析每一行数据
    for line in lines:
        print(f"[Info] Processing line: {line.strip()}")
        parts = line.strip().split()
        # 新格式至少应有 7 个部分：时间戳、通道、"ID:"、CAN_ID、帧类型、"Data:"、数据字节...
        if len(parts) < 7:
            print(f"[Warning] Ignored incomplete line: {line.strip()}")
            continue

        try:
            # 提取并处理时间戳，去除中括号
            timestamp_str = parts[0]
            if timestamp_str.startswith("[") and timestamp_str.endswith("]"):
                timestamp_str = timestamp_str[1:-1]
            timestamp = float(timestamp_str)
            # parts[1] 为通道号（此处可记录，但暂未使用）
            channel = parts[1]
            # parts[2] 应为 "ID:"，parts[3] 为 CAN ID
            if parts[2] != "ID:":
                print(f"[Warning] Expected 'ID:' but got {parts[2]} in line: {line.strip()}")
                continue
            can_id = parts[3]
            can_id = str.upper(can_id[2::])# + 'x'
            print('canid', can_id)
            # parts[4] 为帧类型（例如 "扩展帧" 或 "标准帧"）
            frame_type = parts[4]
            # parts[5] 应为 "Data:"
            if parts[5] != "raw_data:":
                print(f"[Warning] Expected 'Data:' but got {parts[5]} in line: {line.strip()}")
                continue
            # 后续部分为数据字节
            raw_data = " ".join(parts[6:])
            print('raw_data', raw_data)
        except Exception as e:
            print(f"[Error] Failed to extract data from line: {e}")
            continue

        # 根据 CAN ID 获取解析器并解析数据
        try:
            #print('——————————————————————————————————————————————————————————————')
            parser_class = get_parser(can_id)
            print(f"[Info] Using parser class: {parser_class.__name__}")
            parser_instance = parser_class(raw_data)
            parsed_fields = parser_instance.parse()
        except Exception as e:
            print(f"[Error] Parsing failed for CAN ID {can_id}: {e}")
            parsed_fields = {}

        # 更新 all_categories 的内容
        for category, content in parsed_fields.items():
            if category in all_categories:
                existing_data = all_categories[category]
                if "timestamp" not in existing_data or timestamp > existing_data["timestamp"]:
                    print(
                        f"[Update] Updating category '{category}' with new timestamp {timestamp}. Previous timestamp: {existing_data.get('timestamp', 0)}")
                    all_categories[category] = {"timestamp": timestamp, "data": content}
                else:
                    print(
                        f"[Skip] Skipping category '{category}' as existing timestamp {existing_data.get('timestamp', 0)} is newer.")
            else:
                print(f"[New] Adding new category '{category}' with timestamp {timestamp}")
                all_categories[category] = {"timestamp": timestamp, "data": content}

    return all_categories


@app.route('/get_can_data', methods=['GET'])
def get_can_data():
    """
    获取所有类别的 CAN 数据（带初始值）
    :return: JSON 格式的解析结果
    """
    global no_data_logged
    print("[Info] API /get_can_data called")
    new_data = read_new_can_lines()
    if not new_data:
        if not no_data_logged:
            print("[Info] No new data available.")
            no_data_logged = True
        return jsonify([]), 204
    no_data_logged = False
    return jsonify(new_data), 200


def init_usb_can():
    global g_thd_run
    gBaud = 0x1c01  # 波特率设置
    DevType = USBCAN_II  # 设备类型号
    DevIdx = 0  # 设备索引号

    ret = lib.VCI_OpenDevice(DevType, DevIdx, 0)
    if ret == 0:
        print("Open device fail")
        exit(0)
    else:
        print("Opendevice success")

    can_threads = []
    for i in range(MAX_CHANNELS):
        init_config = ZCAN_CAN_INIT_CONFIG()
        init_config.AccCode = 0
        init_config.AccMask = 0xFFFFFFFF
        init_config.Reserved = 0
        init_config.Filter = 1
        init_config.Timing0 = gBaud & 0xff
        init_config.Timing1 = gBaud >> 8
        init_config.Mode = 0
        ret = lib.VCI_InitCAN(DevType, 0, i, byref(init_config))
        if ret == 0:
            print(f"InitCAN({i}) fail")
        else:
            print(f"InitCAN({i}) success")

        ret = lib.VCI_StartCAN(DevType, 0, i)
        if ret == 0:
            print(f"StartCAN({i}) fail")
        else:
            print(f"StartCAN({i}) success")

        thread = threading.Thread(target=usb_can_rx_thread, args=(DevType, DevIdx, i,))
        can_threads.append(thread)
        thread.start()
    return DevType, DevIdx, can_threads


if __name__ == '__main__':
    # 初始化USB CAN设备并启动接收线程
    init_usb_can()
    print("[Info] Starting API service (USB CAN real-time data)")
    # 禁用自动重载功能，防止重复初始化设备
    app.run(host='0.0.0.0', port=5001, debug=True, use_reloader=False)
    # 程序退出时停止线程并关闭设备（根据需要添加清理代码）
    g_thd_run = 0
    time.sleep(1)
    ret = lib.VCI_CloseDevice(USBCAN_II, 0)
    if ret == 0:
        print("Closedevice fail")
    else:
        print("Closedevice success")