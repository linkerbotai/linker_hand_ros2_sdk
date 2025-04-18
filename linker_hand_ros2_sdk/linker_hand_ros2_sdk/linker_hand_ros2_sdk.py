#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
'''
Author: HJX
Date: 2025-04-01 13:55:14
LastEditors: Please set LastEditors
LastEditTime: 2025-04-09 18:36:21
FilePath: /linker_hand_ros2_sdk/src/linker_hand_ros2_sdk/linker_hand_ros2_sdk/linker_hand_ros2_sdk.py
Description: 
编译: colcon build --symlink-install
启动命令:ros2 run linker_hand_ros2_sdk linker_hand_sdk
'''
import rclpy                                     # ROS2 Python接口库
from rclpy.node import Node                      # ROS2 节点类
import rclpy.time
from std_msgs.msg import String, Header
from sensor_msgs.msg import JointState
import time,threading, json
from linker_hand_ros2_sdk.LinkerHand.utils.load_write_yaml import LoadWriteYaml
from linker_hand_ros2_sdk.LinkerHand.utils.init_linker_hand import InitLinkerHand
from linker_hand_ros2_sdk.LinkerHand.linker_hand_api import LinkerHandApi
from linker_hand_ros2_sdk.LinkerHand.utils.color_msg import ColorMsg


class LinkerHandRos2SDK(Node):
    def __init__(self, name):
        super().__init__(name)
        self.yaml = LoadWriteYaml()
        self.config = self.yaml.load_setting_yaml()
        self.left_hand_exists = None
        self.right_hand_exists = None
        self.left_hand_sub = None
        self.right_hand_sub = None
        self._init_linker_hand()
        
        # 启动线程，线程内循环发布机械臂状态
        self.thread = threading.Thread(target=self.pub_linker_hand_state)
        self.thread.daemon = True  # 设置为守护线程，主线程退出时自动结束
        self.thread.start()
        time.sleep(0.1)
        if self.left_hand_exists == True:
            self.left_hand_sub = self.create_subscription(
                JointState,
                '/cb_left_hand_control_cmd',
                self.left_hand_cb,
                10  # 队列长度
            )
        print("_-" * 20)
        print(self.left_hand_exists)
        if self.right_hand_exists == True:
            self.right_hand_sub = self.create_subscription(
                JointState,
                '/cb_right_hand_control_cmd',
                self.right_hand_cb,
                10  # 队列长度
            )
        

    def left_hand_cb(self, msg):
        position = list(msg.position)
        self.left_hand_api.finger_move(pose=position)
    def right_hand_cb(self, msg):
        position = list(msg.position)
        self.right_hand_api.finger_move(pose=position)
    def _init_linker_hand(self):
        self.left_hand ,self.left_hand_joint ,self.left_hand_type ,self.left_hand_force ,self.right_hand ,self.right_hand_joint ,self.right_hand_type ,self.right_hand_force,self.setting = InitLinkerHand().current_hand()
        torque=[250,250,250,250,250]
        speed=[120,250,250,250,250]
        
        if self.left_hand == True:
            self.left_hand_exists = True
            self.left_hand_api = LinkerHandApi(hand_type=self.left_hand_type,hand_joint=self.left_hand_joint)
            
            if self.left_hand_joint == "L7":
                torque=[250,250,250,250,250,250,250]
                speed=[120,250,250,250,250,250,250]
                self.left_hand_api.finger_move(pose=[255, 200, 255, 255, 255, 255, 180])
            elif self.left_hand_joint == "L10":
                self.left_hand_api.finger_move(pose=[255, 200, 255, 255, 255, 255, 180, 180, 180, 41])
            elif self.left_hand_joint == "L20":
                self.left_hand_api.finger_move(pose=[255,255,255,255,255,255,10,100,180,240,245,255,255,255,255,255,255,255,255,255])
            elif self.left_hand_joint == "L25":
                self.left_hand_api.finger_move(pose=[75, 255, 255, 255, 255, 176, 97, 81, 114, 147, 202, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255])
            else:
                self.left_hand_api.finger_move(pose=[80] * 5)
            self.left_hand_pub =  self.create_publisher(JointState, "/cb_left_hand_state", 10)
            self.left_hand_info_pub = self.create_publisher(String, "/cb_left_hand_info", 10)
            if self.left_hand_force == True:
                self.left_hand_touch_pub = self.create_publisher(String, "/cb_left_hand_force", 10)
            self.left_hand_api.set_speed(speed=speed)
            ColorMsg(msg=f"设置当前{self.left_hand_joint} {self.left_hand_type}灵巧手speed:{speed}", color="green")
            time.sleep(0.001)
            self.left_hand_api.set_torque(torque=torque)
            ColorMsg(msg=f"设置当前{self.left_hand_joint} {self.left_hand_type}灵巧手torque:{torque}", color="green")
        elif self.right_hand == True:
            self.right_hand_exists = True
            self.right_hand_api = LinkerHandApi(hand_type=self.right_hand_type,hand_joint=self.right_hand_joint)
            
            if self.right_hand_joint == "L7":
                torque=[250,250,250,250,250,250,250]
                speed=[120,250,250,250,250,250,250]
                self.right_hand_api.finger_move(pose=[255, 200, 255, 255, 255, 255, 180])
            elif self.right_hand_joint == "L10":
                self.right_hand_api.finger_move(pose=[255, 200, 255, 255, 255, 255, 180, 180, 180, 41])
            elif self.right_hand_joint == "L20":
                self.right_hand_api.finger_move(pose=[255,255,255,255,255,255,10,100,180,240,245,255,255,255,255,255,255,255,255,255])
            elif self.right_hand_joint == "L25":
                self.right_hand_api.finger_move(pose=[75, 255, 255, 255, 255, 176, 97, 81, 114, 147, 202, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255])
            else:
                self.right_hand_api.finger_move(pose=[250] * 5)
            self.right_hand_pub =  self.create_publisher(JointState, "/cb_right_hand_state", 10)
            self.right_hand_info_pub = self.create_publisher(String, "/cb_right_hand_info", 10)
            if self.right_hand_force == True:
                self.right_hand_touch_pub = self.create_publisher(String, "/cb_right_hand_force", 10)
            self.right_hand_api.set_speed(speed=speed)
            ColorMsg(msg=f"设置当前{self.right_hand_api} {self.right_hand_type}灵巧手speed:{speed}", color="green")
            time.sleep(0.001)
            self.right_hand_api.set_torque(torque=torque)
            ColorMsg(msg=f"设置当前{self.right_hand_api} {self.right_hand_type}灵巧手torque:{torque}", color="green")


    def _create_joint_state_msg(self, position, names=None):
        '''创建JointState类型消息'''
        # 更安全的写法（显式构造 Time 消息）：
        from builtin_interfaces.msg import Time
        now = self.get_clock().now()
        
        if names is None:
            names = []
        msg = JointState()
        msg.header = Header()
        msg.header.stamp = Time(sec=int(now.nanoseconds // 1e9), 
                            nanosec=int(now.nanoseconds % 1e9))
        msg.name = names
        msg.position = list(map(float, position))
        msg.velocity = [0.0] * len(position)
        msg.effort = [0.0] * len(position)
        return msg

    
    def _get_linker_hand_state(self,hand_type="left"):
        if hand_type == "left":
            return self.left_hand_api.get_state()
        if hand_type == "right":
            return self.right_hand_api.get_state()
        
    def pub_linker_hand_state(self):
        '''发布灵巧手状态'''
        rate = 1.0 / 60  # 60 FPS
        while rclpy.ok():
            if self.left_hand_exists == True:
                left_force = self.left_hand_api.get_force()
                left_info = {
                    "left_hand":{
                        "hand_joint": self.left_hand_joint,
                        "speed": self.left_hand_api.get_speed(),
                        "force": left_force,
                        "motor_temperature": self.left_hand_api.get_temperature(),
                        "torque": self.left_hand_api.get_torque()
                    }
                }
                left_state_pos = self._get_linker_hand_state(hand_type="left")
                left_state_msg = self._create_joint_state_msg(position=left_state_pos)
                self.left_hand_pub.publish(left_state_msg)
                data = String()
                data.data = json.dumps(left_info)
                self.left_hand_info_pub.publish(data)
                if self.left_hand_force == True:
                    force_data = String()
                    force_dic = {
                        "force": left_force
                    }
                    force_data.data = json.dumps(force_dic)
                    self.left_hand_touch_pub.publish(force_data)
            if self.right_hand_exists == True:
                right_force = self.right_hand_api.get_force()
                right_info = {
                    "right_hand":{
                        "hand_joint": self.right_hand_joint,
                        "speed": self.right_hand_api.get_speed(),
                        "force": right_force,
                        "motor_temperature": self.right_hand_api.get_temperature(),
                        "torque": self.right_hand_api.get_torque()
                    }
                }
                right_state_pos = self._get_linker_hand_state(hand_type="right")
                right_state_msg = self._create_joint_state_msg(position=right_state_pos)
                self.right_hand_pub.publish(right_state_msg)
                data = String()
                data.data = json.dumps(right_info)
                self.right_hand_info_pub.publish(data)
                if self.right_hand_force == True:
                    right_force_data = String()
                    right_force_dic = {
                        "force": right_force
                    }
                    right_force_data.data = json.dumps(right_force_dic)
                    self.right_hand_touch_pub.publish(right_force_data)
            time.sleep(rate)



    


def main(args=None):
    rclpy.init(args=args)
    node = LinkerHandRos2SDK("linker_hand_sdk")
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown() 