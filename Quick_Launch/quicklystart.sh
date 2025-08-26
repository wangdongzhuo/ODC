#!/bin/bash
while true; do
    echo "========== 启动所有服务 =========="
    # 并行启动所有服务
    sudo /home/songyuant/anaconda3/envs/riskas/bin/python3 /home/songyuant/PycharmProjects/ODCSOFTbackup/ODCSOFT/monitorODC/ODC_data/main/start_all_service.py &
    pid1=$!
    /home/songyuant/anaconda3/envs/riskas/bin/python3 /home/songyuant/PycharmProjects/ODCSOFTbackup/ODCSOFT/monitorODC/riskassessment/API_riskassessment.py &
    pid2=$!
    /home/songyuant/anaconda3/envs/riskas/bin/python3 /home/songyuant/PycharmProjects/ODCSOFTbackup/ODCSOFT/monitorODC/call_monitor_service.py &
    pid3=$!
    /home/songyuant/anaconda3/envs/riskas/bin/python3 /home/songyuant/PycharmProjects/ODCSOFTbackup/ODCSOFT/monitorODC/get_odd_api.py &
    pid4=$!
    /home/songyuant/anaconda3/envs/riskas/bin/python3 /home/songyuant/PycharmProjects/ODCSOFTbackup/ODCSOFT/monitorODC/save_odd_to_device_api.py &
    pid5=$!
    /home/songyuant/anaconda3/envs/riskas/bin/python3 /home/songyuant/PycharmProjects/ODCSOFTbackup/ODCSOFT/monitorODC/send_cloud_ODC.py &
    pid6=$!

    # 等待任意一个后台进程退出
    wait -n
    exit_code=$?
    echo "检测到进程异常退出 (错误码: $exit_code)，即将重启所有服务..."

    # 终止所有后台进程（包括仍在运行的）
    echo "终止遗留进程..."
    sudo kill -9 $pid1 $pid2 $pid3 $pid4 $pid5 $pid6 2>/dev/null
    wait $pid1 $pid2 $pid3 $pid4 $pid5 $pid6 2>/dev/null  # 确保进程终止
#    sudo kill -9 $pid1 $pid2 $pid3 $pid4 $pid5 2>/dev/null
#    wait $pid1 $pid2 $pid3 $pid4 $pid5 2>/dev/null  # 确保进程终止

    # 延迟重启避免资源竞争
    echo "等待 1 秒后重启..."
    sleep 1
done