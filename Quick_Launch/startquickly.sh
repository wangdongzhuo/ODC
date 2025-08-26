#!/bin/bash
# 启动每个脚本在独立的终端窗口中
#gnome-terminal -- bash -c "sudo /home/songyuant/anaconda3/envs/riskas/bin/python3 /home/songyuant/PycharmProjects/ODCSOFTbackup/ODCSOFT/monitorODC/ODC_data/main/start_all_service.py; exec bash"
gnome-terminal -- bash -c "/home/songyuant/anaconda3/envs/riskas/bin/python3 /home/songyuant/PycharmProjects/ODCSOFTbackup/ODCSOFT/monitorODC/ODC_data/main/start_all_service.py; exec bash"
gnome-terminal -- bash -c "python /home/songyuant/PycharmProjects/ODCSOFTbackup/ODCSOFT/monitorODC/riskassessment/API_riskassessment.py; exec bash"
gnome-terminal -- bash -c "python /home/songyuant/PycharmProjects/ODCSOFTbackup/ODCSOFT/monitorODC/riskassessment/riskcallapi.py; exec bash"
###wait
#gnome-terminal -- bash -c "python /home/songyuant/PycharmProjects/ODCSOFTbackup/ODCSOFT/monitorODC/call_monitor_service.py; exec bash"
#
#gnome-terminal -- bash -c "python /home/songyuant/PycharmProjects/ODCSOFTbackup/ODCSOFT/monitorODC/get_odd_api.py; exec bash"
#
#gnome-terminal -- bash -c "python /home/songyuant/PycharmProjects/ODCSOFTbackup/ODCSOFT/monitorODC/save_odd_to_device_api.py; exec bash"
#
#gnome-terminal -- bash -c "python /home/songyuant/PycharmProjects/ODCSOFTbackup/ODCSOFT/monitorODC/send2cloud/send_cloud_ODC.py; exec bash"
###wait
