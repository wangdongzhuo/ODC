import requests
import json
import time  # 用于循环定时

def json_string_to_dict(json_string: str) -> dict:
    """
    将 JSON 格式的字符串转换为字典。

    :param json_string: JSON 格式的字符串
    :return: 转换后的字典
    """
    try:
        # 使用 json.loads 将字符串解析为字典
        result = json.loads(json_string)
        return result
    except json.JSONDecodeError as e:
        # 捕获解析错误并输出提示
        print(f"JSON 解析错误: {e}")
        return {}

class Weather:  # 天气
    def __init__(self, name):
        self.name = name

class Roadlinestate1:  # 道路标线 左车道线状态1、2
    def __init__(self, distance, heading, curvature, curvaturerate, confidence, launchstate):
        self.distance = distance  # 摄像头到车道线的距离
        self.heading = heading  # 车道线斜率
        self.curvature = curvature  # 车道线曲率
        self.curvaturerate = curvaturerate  # 车道线曲率变化率
        self.confidence = confidence  # 置信度
        self.launchstate = launchstate

    @classmethod
    def roadline1(cls, can_data):
        roaddata1 = can_data["左车道线状态1"]['data']
        if roaddata1 != {}:
            Roadlinestate1.launchstate = True
            Roadlinestate1.distance = roaddata1["摄像头距离左车道线距离"]['数值']
            Roadlinestate1.heading = roaddata1["左车道线斜率"]['数值']
            Roadlinestate1.curvature = roaddata1["左车道线曲率"]['数值']
            Roadlinestate1.curvaturerate = roaddata1["左车道线的曲率变化率"]['数值']
            Roadlinestate1.confidence = can_data["左车道线状态2"]['data']["左车道线置信度"]['数值']
        else:
            Roadlinestate1.launchstate = False
            Roadlinestate1.confidence = 0.1

class Roadlinestate2:  # 道路标线 右车道线状态1、2
    def __init__(self, distance, heading, curvature, curvaturerate, confidence, launchstate):
        self.distance = distance  # 摄像头到车道线的距离
        self.heading = heading  # 车道线斜率
        self.curvature = curvature  # 车道线曲率
        self.curvaturerate = curvaturerate  # 车道线曲率变化率
        self.confidence = confidence  # 置信度
        self.launchstate = launchstate

    @classmethod
    def roadline2(cls, can_data):
        roaddata2 = can_data["右车道线状态1"]['data']
        if roaddata2 != {}:
            Roadlinestate2.launchstate = True
            Roadlinestate2.distance = roaddata2["摄像头距离右车道线距离"]['数值']
            Roadlinestate2.heading = roaddata2["右车道线斜率"]['数值']
            Roadlinestate2.curvature = roaddata2["右车道线曲率"]['数值']
            Roadlinestate2.curvaturerate = roaddata2["右车道线的曲率变化率"]['数值']
            Roadlinestate2.confidence = can_data["右车道线状态2"]['data']["右车道线置信度"]['数值']
        else:
            Roadlinestate2.launchstate = False
            Roadlinestate2.confidence = 0.9

class EgoTrunangle:  # 自车方向盘转角 控制转向系统报文
    def __init__(self, angle, launchstate):
        self.angle = angle
        self.launchstate = launchstate

    @classmethod
    def egotrunangle(cls, can_data):
        egoangledata = can_data['控制转向系统报文']['data']
        if egoangledata != {}:
            EgoTrunangle.launchstate = True
            EgoTrunangle.angle = can_data["方向盘角度指令"]['数值']
        else:
            EgoTrunangle.launchstate = False


class Egovelocity:  # 自车速度 驱动状态报文报文
    def __init__(self, v, x, y, launchstate):
        self.v = v  # 速度
        self.x = x  # 纵向
        self.y = y  # 横向
        self.launchstate = launchstate

    @classmethod
    def egov(cls,can_data):
        egovdata = can_data['车辆车速报文']['data']
        if egovdata != {}:
            Egovelocity.launchstate = True
            Egovelocity.v = egovdata['车速值']
        else:
            Egovelocity.launchstate = False

class CardoorState:  # 车门状态 智能车辆状态反馈包含车门信息
    def __init__(self, doornumber, state, warn, launchstate):
        self.doornumber = doornumber  # 车门的位置
        self.state = state  # 车门的状态
        self.warn = warn  # 警告
        self.launchstate = launchstate
    @classmethod
    def cardoor(cls, can_data):
        cardoordata = can_data['智能车辆状态反馈']['data']
        if cardoordata != {}:
            CardoorState.launchstate = True
            CardoorState.doornumber = list(cardoordata['车门状态'].keys())
            state1 = True if cardoordata['车门状态']['中门'] == "门已经关" else False
            state2 = True if cardoordata['车门状态']['前门'] == "门已经关" else False
            state3 = True if cardoordata['车门状态']['后门钥匙'] == "门已经关" else False
            CardoorState.state = state1 and state2 and state3
            CardoorState.warn = True
            for i in cardoordata['报警状态'].keys():
                warnvalue = True if cardoordata['报警状态'][i] == '未报警' else False
                CardoorState.warn = CardoorState.warn and warnvalue
        else:
            CardoorState.launchstate = False

class FaultIC:  # 协同控制器故障类型与等级 协同控制器系统故障报文
    def __init__(self, level, totallevel, ftype, launchstate):
        self.level = level  # 部件故障等级（越高越严重）
        self.totallevel = totallevel  # 故障等级总数
        self.ftype = ftype  # 故障类型
        self.launchstate = launchstate

    @classmethod
    def faultic(cls, can_data):
        faulticdata = can_data['协同控制器系统故障报文']['data']
        if faulticdata != {}:
            FaultIC.totallevel1 = 3
            FaultIC.totallevel2 = 3
            FaultIC.launchstate = True
            # if faulticdata['部件故障等级']
            if faulticdata['故障类型'] == "NULL 无效值":
                FaultIC.ftype = 0
            elif faulticdata['故障类型'] == "此类故障属于，有故障时显示，故障消失则不显示":
                FaultIC.ftype = 1
            elif faulticdata['故障类型'] == "此类故障属于，系统重新上电或初始化，则故障显示消失":
                FaultIC.ftype = 2
            elif faulticdata['故障类型'] == "此类故障属于，一旦出现则被锁定，需要后台维修后，方可消除故障显示":
                FaultIC.ftype = 3
        else:
            FaultIC.launchstate = False

class Pedalstate:  # 踏板位置 驱动状态报文报文
    def __init__(self, acl, brk, launchstate):
        self.acl = acl  # 加速踏板
        self.brk = brk  # 制动踏板
        self.launchstate = launchstate

    @classmethod
    def pedal(cls, can_data):
        pedaldata = can_data['驱动状态报文']['data']
        if pedaldata != {}:
            Pedalstate.launchstate = True
            Pedalstate.acl = pedaldata['模拟加速踏板当前实际位置']
            Pedalstate.brk = pedaldata['模拟制动踏板当前实际位置']
        else:
            Pedalstate.launchstate = False

# class Gears:  # 档位信息 域控制器基础信息 1
#     def __init__(self, gear, pgear):
#         self.gear = gear  # 当前档位：R，N，D
#         self.pgear = pgear  # P档状态

class SystemFault:  # 系统故障等级(其中包含压力，制动)
    def __init__(self, lowpressure, highpressure, breakstate,
                 lowpressure_tlevel, highpressure_tlevel, breakstate_tlevel, launchstate):
        self.lowpressure = lowpressure  # 高压系统故障等级
        self.highpressure = highpressure  # 低压系统等级
        self.breakstate = breakstate  # 制动系统等级
        self.lowpressure_tlevel = lowpressure_tlevel
        self.highpressure_tlevel = highpressure_tlevel
        self.breakstate_tlevel = breakstate_tlevel
        self.launchstate = launchstate
    @classmethod
    def systemF(cls, can_data):
        systemFdata = can_data['域控制器基础信息2']['data']
        if systemFdata != {}:
            SystemFault.launchstate = True
            SystemFault.lowpressure_tlevel = 3
            SystemFault.highpressure_tlevel = 4
            SystemFault.breakstate_tlevel = 3
            if systemFdata['低压系统故障'] == '无故障':
                SystemFault.lowpressure = 0
            elif systemFdata['低压系统故障'] == '一级故障':
                SystemFault.lowpressure = 1
            elif systemFdata['低压系统故障'] == '二级故障':
                SystemFault.lowpressure = 2
            elif systemFdata['低压系统故障'] == '三级故障':
                SystemFault.lowpressure = 3
            else:
                SystemFault.lowpressure = 0
            if systemFdata['高压系统故障'] == '无故障':
                SystemFault.highpressure = 0
            elif systemFdata['高压系统故障'] == '一级故障':
                SystemFault.highpressure = 1
            elif systemFdata['高压系统故障'] == '二级故障':
                SystemFault.highpressure = 2
            elif systemFdata['高压系统故障'] == '三级故障':
                SystemFault.highpressure = 3
            elif systemFdata['高压系统故障'] == '四级故障':
                SystemFault.highpressure = 4
            else:
                SystemFault.highpressure = 0
            if systemFdata['制动系统故障'] == '无故障':
                SystemFault.breakstate = 0
            elif systemFdata['制动系统故障'] == '一级故障':
                SystemFault.breakstate = 1
            elif systemFdata['制动系统故障'] == '二级故障':
                SystemFault.breakstate = 2
            elif systemFdata['制动系统故障'] == '三级故障':
                SystemFault.breakstate = 3
            else:
                SystemFault.breakstate = 0
        else:
            SystemFault.launchstate = False

# class AutoFunlimit:  # 自动功能限制
#     def __init__(self, enterlimit, quitreason):
#         self.enterlimit = enterlimit  # 进入自动功能限制 域控制器基础信息 2
#         self.quitreason = quitreason  # 退出自动功能原因

class L2FuStfeedback:  # L2功能状态反馈
    def __init__(self, accstate, accnotlaunch, accquitreason,
                 lkastate, lkanotlaunch, lkaquitreason, ldwstate,
                 cmsaebstate, cmsaebwarninglevel, launchstate):
        self.accstate = accstate  # ACC状态
        self.accnotlaunch = accnotlaunch  # ACC无法启动原因
        self.accquitreason = accquitreason  # ACC退出原因
        self.lkastate = lkastate  # LKA状态
        self.lkanotlaunch = lkanotlaunch  # LKA无法启动原因
        self.lkaquitreason = lkaquitreason  # LKA退出原因
        self.ldwstate = ldwstate  # LDW状态
        self.cmsaebstate = cmsaebstate   # CMS与AEB状态
        self.cmsaebwarninglevel = cmsaebwarninglevel  # CMS与AEB报警等级
        self.launchstate = launchstate  # L2功能是否开启
    @classmethod
    def L2Funst(cls, can_data):
        datacan = can_data['L2功能状态反馈']['data']
        if datacan == {}:
            L2FuStfeedback.launchstate = False
        else:
            L2FuStfeedback.launchstate = True
            if datacan['ACC工作状态'] == "故障":
                L2FuStfeedback.accstate = False
            else:
                L2FuStfeedback.accstate = True
            if datacan['LKA工作状态'] == "故障":
                L2FuStfeedback.lkastate = False
            else:
                L2FuStfeedback.lkastate = True
            if datacan['LDW工作状态'] == "故障":
                L2FuStfeedback.ldwstate = False
            else:
                L2FuStfeedback.ldwstate = True
            if datacan['CMS&AEB系统工作状态'] == "故障":
                L2FuStfeedback.cmsaebstate = False
            else:
                L2FuStfeedback.cmsaebstate = True

class DDTfeedbackstate:  # 驾驶人状态
    def __init__(self, safetybelt, driverleft, warnstate, tstatelevel, launchstate, tstate):
        self.safetybelt = safetybelt  # 安全带状态
        self.driverleft = driverleft  # 司机离座报警
        self.warnstate = warnstate  # 司机异常状态
        self.tstatelevel = tstatelevel
        self.launchstate = launchstate
        self.tstate = tstate
    @classmethod
    def DDTst(cls, can_data, driver_data):
        carctrldata = can_data['智能控制状态反馈']['data']
        if carctrldata != {}:
            DDTfeedbackstate.launchstate1 = True
            DDTfeedbackstate.safetybelt = True if carctrldata['报警状态']['安全带'] == '未激活' else False
            DDTfeedbackstate.driverleft = True if carctrldata['报警状态']['司机离座'] == '未激活' else False
        else:
            DDTfeedbackstate.launchstate1 = False
        #print(driver_data)
        print(driver_data['state_description'],'driver_data')
        print(driver_data['state_code'],'driver_data_code')
        if driver_data['state_description'] != {}:
            DDTfeedbackstate.launchstate2 = True
            DDTfeedbackstate.tstatelevel = 4
            if driver_data['state_code'] == '0x00':
                DDTfeedbackstate.warnstate = 0
            elif driver_data['state_code'] == '0x07' or '0x01' or '0x02' or '0x09' or '0x0c' or '0x08':
                DDTfeedbackstate.warnstate = 1
            elif driver_data['state_code'] == '0x04' or '0x05':
                DDTfeedbackstate.warnstate = 2
            elif driver_data['state_code'] == '0x06' or '0x03' or '0x09':
                DDTfeedbackstate.warnstate = 3
            elif driver_data['state_code'] == '0x0a' or '0x0b':
                DDTfeedbackstate.warnstate = 4
        else:
            DDTfeedbackstate.launchstate2 = False
        DDTfeedbackstate.launchstate = DDTfeedbackstate.launchstate1 and DDTfeedbackstate.launchstate2
        # print(DDTfeedbackstate.launchstate,'DDTfeedbackstate.launchstate')
        if DDTfeedbackstate.launchstate:
            # 风险等级规则：
            # 驾驶员监测系统传入驾驶员异常状态：
            # 无报警为0 【0级】
            # 检测不到人脸与未系安全带与CAN数据搭配 【100类、等级四】
            # 打盹、闭眼、遮挡摄像头（疲劳驾驶）【等级三】
            # 低头、转头（属于视线不集中在前方）【等级二】
            # 喝水、抽烟、打电话、佩戴遮阳镜、打哈欠【等级一】
            if DDTfeedbackstate.warnstate == 4 or DDTfeedbackstate.safetybelt == False or DDTfeedbackstate.driverleft == False:
                DDTfeedbackstate.tstate = 4
            else:
                DDTfeedbackstate.tstate = DDTfeedbackstate.warnstate
        else:
            DDTfeedbackstate.tstate = False
        # print(DDTfeedbackstate.tstate,'DDTfeedbackstate.tstate')

class Temperature:  # 包含温度与轮胎压力
    def __init__(self, outcartemperature, wheelpresure, launchstate):
        self.outcartemperature = outcartemperature  # 车外温度
        self.wheelpresure = wheelpresure
        self.launchstate = launchstate

    @classmethod
    def tempre(cls, can_data):
        tempredata = can_data['胎压监控系统状态']['data']
        if tempredata != {}:
            Temperature.launchstate = True
            Temperature.outcartemperature = True if float(tempredata['轮胎信息']['温度']['数值']) <= 55 else False
            Temperature.wheelpresure = tempredata['轮胎信息']['压力']['数值']
        else:
            Temperature.launchstate = False

# 主目标信息包含目标物信息和组件故障信息
class Mainobstaclformation:  # 感知主目标物信息
    def __init__(self, mainobstacletype, posx, posy, relvelx, relvely, launchstate):
        self.mainobstacletype = mainobstacletype  # 主目标物类型
        self.posx = posx  # 纵向相对距离
        self.posy = posy  # 横向相对距离
        self.relvelx = relvelx  # 纵向相对速度
        self.relvely = relvely  # 横向相对速度
        self.launchstate = launchstate

    @classmethod
    def mainob(cls, can_data):
        mainobdata = can_data['主目标信息']['data']
        # print("mainobdata", can_data['主目标信息'])
        if mainobdata != {}:
            Mainobstaclformation.launchstate = True
            Mainobstaclformation.mainobstacletype = mainobdata['主目标标志类型']["数值"]
            Mainobstaclformation.posx = mainobdata['主目标相对位置X']["数值"]
            Mainobstaclformation.posy = mainobdata['主目标相对位置Y']["数值"]
            Mainobstaclformation.relvelx = mainobdata['与主目标相对速度X']["数值"]
            Mainobstaclformation.relvely = mainobdata['与主目标相对速度Y']["数值"]
            # print("PFC_Main_Obstacle_Pos_X", Mainobstaclformation.posx)
        else:
            Mainobstaclformation.launchstate = False
            # print("没有主目标的数值")

class Preceivepartstate:  # 感知组件故障信息
    def __init__(self, camera, radar, vehicleconnect, fusion, launchstate):
        self.camera = camera  # 摄像头连接
        self.radar = radar  # 雷达
        self.vehicleconnect = vehicleconnect  # 车辆连接
        self.fusion = fusion  # 感知融合
        self.launchstate = launchstate

    @classmethod
    def prece(cls, can_data):
        precedata = can_data['主目标信息']['data']
        if precedata != {}:
            Preceivepartstate.launchstate = True
            # Preceivepartstate.camera = True if precedata['PFC_Camera_Connect_Fault'] == "无故障" else False
            # Preceivepartstate.camera = True if precedata['PFC_Radar_Fault'] == "无故障" else False
            Preceivepartstate.vehicleconnect = True if precedata['车辆连接故障']['状态'] == "无故障" else False
            Preceivepartstate.fusion = True if precedata['感知融合故障']['状态'] == "无故障" else False
        else:
            Preceivepartstate.launchstate = False

def dataupdate(can_data, driver_data):
    Roadlinestate1.roadline1(can_data)
    Roadlinestate2.roadline2(can_data)
    EgoTrunangle.egotrunangle(can_data)
    Egovelocity.egov(can_data)
    CardoorState.cardoor(can_data)
    FaultIC.faultic(can_data)
    Pedalstate.pedal(can_data)
    SystemFault.systemF(can_data)
    L2FuStfeedback.L2Funst(can_data)
    DDTfeedbackstate.DDTst(can_data, driver_data)
    Temperature.tempre(can_data)
    Mainobstaclformation.mainob(can_data)
    Preceivepartstate.prece(can_data)


if __name__ == "__main__":
    pass