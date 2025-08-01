#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='linker_hand_ros2_sdk',
            executable='linker_hand_sdk',
            name='linker_hand_sdk_left',
            output='screen',
            parameters=[{
                'hand_type': 'left',
                'hand_joint': "L10", # 这里需要修改为实际Linker Hand的型号 L7、L10、L20、L21、L25
                'is_touch': True, # 是否带有压力传感器
                'can': 'can0',
            }],
        ),

        Node(
            package='linker_hand_ros2_sdk',
            executable='linker_hand_sdk',
            name='linker_hand_sdk_right',
            output='screen',
            parameters=[{
                'hand_type': 'right',
                'hand_joint': "L10", # 这里需要修改为实际Linker Hand的型号 L7、L10、L20、L21、L25
                'is_touch': True, # 是否带有压力传感器
                'can': 'can1',
            }],
        ),
    ])
