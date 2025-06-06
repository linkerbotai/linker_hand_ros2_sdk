import sys
import time
import can
import threading
from enum import Enum

class FrameProperty(Enum):
    INVALID_FRAME_PROPERTY = 0x00  # 无效的can帧属性 | 无返回
    JOINT_PITCH_R = 0x01           # 短帧俯仰角-手指根部弯曲 | 返回本类型数据
    JOINT_YAW_R = 0x02             # 短帧航向角-手指横摆，控制间隙 | 返回本类型数据
    JOINT_ROLL_R = 0x03            # 短帧横滚角-只有大拇指副用到了 | 返回本类型数据
    JOINT_TIP_R = 0x04             # 短帧指尖角度控制 | 返回本类型数据
    JOINT_SPEED_R = 0x05           # 短帧速度 电机运行速度控制 | 返回本类型数据
    JOINT_CURRENT_R = 0x06         # 短帧电流 电机运行电流反馈 | 返回本类型数据
    JOINT_FAULT_R = 0x07           # 短帧故障 电机运行故障反馈 | 返回本类型数据
    REQUEST_DATA_RETURN = 0x09      # 请求数据返回 | 返回所有数据
    JOINT_PITCH_NR = 0x11           # 俯仰角-手指根部弯曲 | 不返回本类型数据
    JOINT_YAW_NR = 0x12             # 航向角-手指横摆，控制间隙 | 不返回本类型数据
    JOINT_ROLL_NR = 0x13            # 横滚角-只有大拇指副用到了 | 不返回本类型数据
    JOINT_TIP_NR = 0x14             # 指尖角度控制 | 不返回本类型数据
    JOINT_SPEED_NR = 0x15           # 速度 电机运行速度控制 | 不返回本类型数据
    JOINT_CURRENT_NR = 0x16         # 电流 电机运行电流反馈 | 不返回本类型数据
    JOINT_FAULT_NR = 0x17           # 故障 电机运行故障反馈 | 不返回本类型数据
    HAND_UID = 0xC0                 # 设备唯一标识码 只读 --------
    HAND_HARDWARE_VERSION = 0xC1    # 硬件版本 只读 --------
    HAND_SOFTWARE_VERSION = 0xC2    # 软件版本 只读 --------
    HAND_COMM_ID = 0xC3             # 设备ID 可读写 1字节
    HAND_SAVE_PARAMETER = 0xCF       # 保存参数 只写 --------


class LinkerHandL20Can:
    def __init__(self, can_channel='can0', baudrate=1000000, can_id=0x28):
        self.can_id = can_id
        self.running = True
        self.x05, self.x06, self.x07 = [],[],[]
        
        # 根据操作系统初始化 CAN 总线
        if sys.platform == "linux":
            self.bus = can.interface.Bus(
                channel=can_channel, interface="socketcan", bitrate=baudrate, 
                can_filters=[{"can_id": can_id, "can_mask": 0x7FF}]
            )
        elif sys.platform == "win32":
            self.bus = can.interface.Bus(
                channel='PCAN_USBBUS1', interface='pcan', bitrate=baudrate, 
                can_filters=[{"can_id": can_id, "can_mask": 0x7FF}]
            )
        else:
            raise EnvironmentError("Unsupported platform for CAN interface")

        # 初始化数据存储
        self.x01, self.x02, self.x03, self.x04 = [[0.0] * 5 for _ in range(4)]
        self.normal_force, self.tangential_force, self.tangential_force_dir, self.approach_inc = \
            [[0.0] * 5 for _ in range(4)]

        # 启动接收线程
        self.receive_thread = threading.Thread(target=self.receive_response)
        self.receive_thread.daemon = True
        self.receive_thread.start()

    def send_command(self, frame_property, data_list):
        print("66666")
        """
        发送命令到 CAN 总线
        :param frame_property: 数据帧属性
        :param data_list: 数据载荷
        """
        frame_property_value = int(frame_property.value) if hasattr(frame_property, 'value') else frame_property
        data = [frame_property_value] + [int(val) for val in data_list]
        msg = can.Message(arbitration_id=self.can_id, data=data, is_extended_id=False)
        try:
            self.bus.send(msg)
            print(f"Message sent: ID={hex(self.can_id)}, Data={data}")
        except can.CanError as e:
            print(f"Failed to send message: {e}")

    def receive_response(self):
        """
        接收并处理 CAN 总线的响应消息
        """
        while self.running:
            try:
                msg = self.bus.recv(timeout=1.0)  # 阻塞接收，1 秒超时
                if msg:
                    self.process_response(msg)
            except can.CanError as e:
                print(f"Error receiving message: {e}")

    def set_finger_base(self, angles):
        self.send_command(FrameProperty.JOINT_PITCH_R, angles)

    def set_finger_tip(self, angles):
        self.send_command(FrameProperty.JOINT_TIP_R, angles)

    def set_finger_middle(self, angles):
        self.send_command(FrameProperty.JOINT_YAW_R, angles)

    def set_thumb_roll(self, angle):
        self.send_command(FrameProperty.JOINT_ROLL_R, angle)

    def send_command(self, frame_property, data_list):
        frame_property_value = int(frame_property.value) if hasattr(frame_property, 'value') else frame_property
        data = [frame_property_value] + [int(val) for val in data_list]
        
        msg = can.Message(arbitration_id=self.can_id, data=data, is_extended_id=False)
        try:
            self.bus.send(msg)
        except can.CanError:
            print("Message NOT sent")
        time.sleep(0.002)

    def set_joint_pitch(self, frame, angles):
        self.send_command(frame, angles)

    def set_joint_yaw(self, angles):
        self.send_command(0x02, angles)

    def set_joint_roll(self, thumb_roll):
        self.send_command(0x03, [thumb_roll, 0, 0, 0, 0])

    def set_joint_speed(self, speed):
        self.x05 = speed
        self.send_command(0x05, speed)
    def set_electric_current(self, e_c=[]):
        self.send_command(0x06, e_c)

    def get_normal_force(self):
        self.send_command(0x20,[])

    def get_tangential_force(self):
        self.send_command(0x21,[])


    def get_tangential_force_dir(self):
        self.send_command(0x22,[])

    def get_approach_inc(self):
        self.send_command(0x23,[])




    def get_electric_current(self, e_c=[]):
        self.send_command(0x06, e_c)
    
    def request_device_info(self):
        self.send_command(0xC0, [0])
        self.send_command(0xC1, [0])
        self.send_command(0xC2, [0])

    def save_parameters(self):
        self.send_command(0xCF, [])
    def process_response(self, msg):
        if msg.arbitration_id == self.can_id:
            frame_type = msg.data[0]
            response_data = msg.data[1:]
            if frame_type == 0x01:
                self.x01 = list(response_data)
                # print("x01")
                # print(self.x01)
            elif frame_type == 0x02:
                self.x02 = list(response_data)
                # print("x02")
                # print(self.x02)
            elif frame_type == 0x03:
                self.x03 = list(response_data)
                # print("x03")
                # print(self.x03)
            elif frame_type == 0x04:
                self.x04 = list(response_data)
                # print("x04")
                # print(self.x04)
            elif frame_type == 0xC0:
                print(f"Device ID info: {response_data}")
                if self.can_id == 0x28:
                    self.right_hand_info = response_data
                elif self.can_id == 0x27:
                    self.left_hand_info = response_data
            elif frame_type == 0x05:
                #ColorMsg(msg=f"速度设置为：{list(response_data)}", color="yellow")
                self.x05 = list(response_data)
                
            elif frame_type == 0x06:
                #ColorMsg(msg=f"当前电流状态：{list(response_data)}")
                self.x06 = list(response_data)
            elif frame_type == 0x07:
                #ColorMsg(msg=f"电机故障状态反馈：{list(response_data)}", color="yellow")
                self.x07 = list(response_data)
            elif frame_type == 0x20:
                #ColorMsg(msg=f"五指法向压力：{list(response_data)}")
                d = list(response_data)
                self.normal_force = [float(i) for i in d] 
            elif frame_type == 0x21:
                #ColorMsg(msg=f"五指切向压力：{list(response_data)}")
                d = list(response_data)
                self.tangential_force = [float(i) for i in d]
            elif frame_type == 0x22:
                #ColorMsg(msg=f"五指切向压力方向：{list(response_data)}")
                d = list(response_data)
                self.tangential_force_dir = [float(i) for i in d]
            elif frame_type == 0x23:
                #ColorMsg(msg=f"五指接近度：{list(response_data)}")
                d = list(response_data)
                self.approach_inc = [float(i) for i in d]
    def pose_slice(self, p):
        """将关节数组切片为手指动作数组"""
        try:
            finger_base = [int(val) for val in p[0:5]]   # 手指根部
            yaw_angles = [int(val) for val in p[5:10]]    # 横摆
            thumb_yaw = [int(val) for val in p[10:15]]     # 拇指向手心横摆，其他为0
            finger_tip = [int(val) for val in p[15:20]]    # 指尖弯曲
            return finger_base, yaw_angles, thumb_yaw, finger_tip
        except Exception as e:
            print(e)
            #ColorMsg(msg="手部关节数据必须是正整数，范围:0~255之间", color="red")
    def set_joint_positions(self, position):
        if len(position) != 20:
            print("L20手指关节长度不对")
            return
        finger_base, yaw_angles, thumb_yaw, finger_tip = self.pose_slice(position)
        self.set_thumb_roll(thumb_yaw) # 大拇想手心横摆指移动
        self.set_finger_tip(finger_tip) # 指尖移动
        self.set_finger_base(finger_base) # 手指根部移动
        self.set_finger_middle(yaw_angles) # 横摆移动
    def set_speed(self, speed=[]):
        self.send_command(0x05,speed)
    def set_torque(self, torque=[]):
        '''设置扭矩 L20暂不支持'''
        print("设置扭矩 L20暂不支持")
    def set_current(self, current=[]):
        '''设置当前电流'''
        self.set_electric_current(e_c=current)
    def get_version(self):
        '''获取版本 当前不支持'''
        return [0] * 5
    def get_current_status(self):
        '''获取当前手指关节状态'''
        self.send_command(0x01,[])
        self.send_command(0x02,[])
        self.send_command(0x03,[])
        self.send_command(0x04,[])
        return self.x01 + self.x02 + self.x03 + self.x04
    def get_force(self):
        return [self.normal_force,self.tangential_force , self.tangential_force_dir , self.approach_inc]
    def get_speed(self):
        '''获取当前电机速度'''
        self.send_command(0x05, [0])
        time.sleep(0.001)
        return self.x05
    def get_current(self):
        '''获取当前电流'''
        self.send_command(0x06, [0])
        return self.x06
    def get_torque(self):
        '''获取当前电机扭矩 L20暂不支持'''
        return [0] * 5
    def get_fault(self):
        return self.x07
    def get_temperature(self):
        '''获取电机温度 L20暂不支持'''
        return [0]* 10
    def clear_faults(self):
        '''清除电机故障'''
        self.send_command(0x07, [1, 1, 1, 1, 1])
    def get_faults(self):
        '''获取电机故障码'''
        self.send_command(0x07, [])
        return self.x07
    def get_force(self):
        '''获取压感数据'''
        return [self.normal_force,self.tangential_force,self.tangential_force_dir,self.approach_inc]
    def close_can_interface(self):
        if self.bus:
            self.bus.shutdown()  # 关闭 CAN 总线

