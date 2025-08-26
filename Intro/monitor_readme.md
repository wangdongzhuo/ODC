# ODC Data Project

## 项目简介
该项目旨在实现驾驶员状态、CAN 数据、云端和高精地图等相关数据的实时模拟与预处理功能，并进行监测

---

## 文件结构

### 1. `ODC_data`
- 存储原始数据，包括驾驶员状态、CAN 数据、地图文件和其他相关信息。用于作为数据模拟和预处理的输入。
  -`data-real-time/`
    - 存储实时生成的数据结果，包括实时更新的驾驶员状态、CAN 数据、云端数据及地图文件。
  -`data-original`
    - 存储数据帧，包括车、驾驶员状态、高精地图。
  -`main/`
    - `parsers/`
      -存放CAN总线映射规则
    -main下面各个py文件是接口api_service文件，以及调用相应接口的call_api文件。在使用时，需要在各个接口中修改`data-real-time`文件路径

### 2. `ODCruledata`
- 存储ODC元素监测规则，此处使用不需要改动


### 3. `使用说明`
- 1.首先运行'\ODC_data\main\start_all_service.py'文件,一件启动所有的api_service，并调用相关的call_api文件
- 2.\monitorODC\call_monitor_service.py则定义了许多监测的接口
- 3.\monitorODC\test_api.py中给出了一个接口，可以用于测试\monitorODC\call_monitor_service.py文件中各个接口。




