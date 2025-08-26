使用方法：
1.终端启动start_all_service服务（发送数据），分别是：
    - python monitorODC/ODC_data/main/start_all_service.py（ODC_data/main/api_service_驾驶员状态.py）
2.终端启动数据模拟，分别是：
    - python simulate_real_time_data_驾驶员状态.py（ODC_data/main/simulate_real_time_data_驾驶员状态.py）
    - python simulate_real_time_data_CAN.py（ODC_data/main/simulate_real_time_data_CAN.py）
3.终端启动风险评估API服务（接收数据），分别是：
    - python monitorODC/riskassessment/API_riskassessment.py
    - python monitorODC/riskassessment/riskcallapi.py
说明：
驾驶员异常状态等级定义位于ODCelement.py中分为5个等级，0,1,2,3,4 目前均分风险数值
均分逻辑位于API_riskassessment.py 函数 levelrisk()中
