#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
'''
Author: HJX
Date: 2025-04-01 14:09:21
LastEditors: Please set LastEditors
LastEditTime: 2025-04-11 09:15:31
FilePath: /Linker_Hand_SDK_ROS/src/linker_hand_sdk_ros/scripts/LinkerHand/utils/open_can.py
Description: 
symbol_custom_string_obkorol_copyright: 
'''
import sys,os,time,subprocess
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from color_msg import ColorMsg
from load_write_yaml import LoadWriteYaml
class OpenCan:
    def __init__(self,load_yaml=None):
        self.yaml = LoadWriteYaml()
        self.password = self.yaml.load_setting_yaml()["PASSWORD"]

    def open_can0(self):
        try:
            # 检查 can0 接口是否已存在并处于 up 状态
            result = subprocess.run(
                ["ip", "link", "show", "can0"],
                check=True,
                text=True,
                capture_output=True
            )
            if "state UP" in result.stdout:
                return 
            # 如果没有处于 UP 状态，则配置接口
            subprocess.run(
                ["sudo", "-S", "ip", "link", "set", "can0", "up", "type", "can", "bitrate", "1000000"],
                input=f"{self.password}\n",
                check=True,
                text=True,
                capture_output=True
            )
            
        except subprocess.CalledProcessError as e:
            pass
        except Exception as e:
            pass
            

    def is_can_up_sysfs(self, interface="can0"):
    # 检查接口目录是否存在
        if not os.path.exists(f"/sys/class/net/{interface}"):
            return False
        # 读取接口状态
        try:
            with open(f"/sys/class/net/{interface}/operstate", "r") as f:
                state = f.read().strip()
            if state == "up":
                return True
        except Exception as e:
            print(f"Error reading CAN interface state: {e}")
            return False