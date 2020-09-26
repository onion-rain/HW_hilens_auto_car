#!/usr/bin/env python
#coding=utf-8
import rospy
#倒入自定义的数据类型
import time
from std_msgs.msg import Int32
from std_msgs.msg import Float64
#from geometry_msgs.msg import Twist
from std_msgs.msg import Bool
import numpy as np
import threading

# 全局变量       
lane_vel = 50                   # 小车转弯值0-100,50为中间 
traffic_light_data= 100
lid_vel = 50
motorspeed = 0
mile_stone = 0.0
lidobj = 0

# 阻塞监听话题
def thread_job():        
    rospy.spin()
# 巡线反馈
def lanecallback(msg):  
    global lane_vel
    lane_vel = msg.data
#雷达反馈
def lidcallback(msg):    
    global lid_vel
    lid_vel = msg.data
def lidobj_callback(msg):
    global lidobj
    lidobj = msg.data
# 交通灯识别反馈
def lightcallback(msg):   
    global traffic_light_data
    traffic_light_data = msg.data
# 电机速度反馈
def motorspeed_callback(msg):  
    global motorspeed
    motorspeed = msg.data
# 里程计反馈
def milestone_callback(msg):
    global mile_stone
    mile_stone = msg.data
# 快速起步函数
def quick_speedup(targetSpeed):
    if motorspeed < (targetSpeed - 6) * 100:
        return targetSpeed + 20
    else:
        return targetSpeed


def kinematicCtrl():
    
    #Publisher 函数第一个参数是话题名称，第二个参数 数据类型，现在就是我们定义的msg 最后一个是缓冲区的大小
    #queue_size: None（不建议）  #这将设置为阻塞式同步收发模式！
    #queue_size: 0（不建议）#这将设置为无限缓冲区模式，很危险！
    #queue_size: 10 or more  #一般情况下，设为10 。queue_size太大了会导致数据延迟不同步。
    
    pub1 = rospy.Publisher('/bluetooth/received/manul', Int32 , queue_size=10)
    pub2 = rospy.Publisher('/auto_driver/send/direction', Int32 , queue_size=10)
    pub3 = rospy.Publisher('/auto_driver/send/speed', Int32 , queue_size=10)
    pub4 = rospy.Publisher('/auto_driver/send/gear', Int32 , queue_size=10)

    manul=0       # 0 - Automatic(自动); 1 - Manual (手动操控)
    speed=20      # SPEED (0～100之间的值)
    direction=50  # 0-LEFT-50-RIGHT-100 (0-49:左转，50:直行，51～100:右转)
    gear=2        # 1 - DRIVE, 2 - NEUTRAL, 3 - PARK, 4 - REVERSE
                  # 1:前进挡 2:空挡 3:停车挡 4:倒挡 0:急刹车
    game_stage = 0  # 用于记录比赛行程阶段,0为初始位置等待绿灯出发,1为绿灯出发
    start_milestone = 0

    rospy.init_node('kinematicCtrl', anonymous=True)        # 初始化节点kinematicCtrl
    
    add_thread = threading.Thread(target = thread_job)     # 阻塞循环接收节点
    add_thread.start()
    
    rate = rospy.Rate(20) # Hz
    rospy.Subscriber("/lane_vel", Int32, lanecallback)         # 订阅巡线转角信息
    rospy.Subscriber("/traffic_light", Int32, lightcallback)  # 订阅交通灯信息
    rospy.Subscriber("/lidangle", Int32, lidcallback)             # 订阅雷达转角信息
    rospy.Subscriber("/lidobj", Int32, lidobj_callback)           
    rospy.Subscriber("/vcu/ActualMotorSpeed", Int32, motorspeed_callback)  #订阅电机速度信息0-10000
    rospy.Subscriber("/ActualMilestone", Float64, milestone_callback)   # 订阅里程计信息
        

    while not rospy.is_shutdown():    
        # 此处以“红灯停、绿灯行”为例，写下逻辑。
        # 绿灯9，停止1，黄灯2，禁速3，解禁速4，快接近人行道5
        # USE (traffic_light_data)
        # TO CHANGE: GEAR, DIRECTION AND SPEED.

        if game_stage == 0:  # 当绿灯亮起，固定方向出发
            if traffic_light_data == 9: 
                start_milestone = mile_stone
                game_stage = 1
        if game_stage == 1:  # 直走x米后，开始巡线
            if (mile_stone - start_milestone) > 0.5:
                game_stage = 2
            else:
                direction = 50
                speed = quick_speedup(50)
                gear = 1
        if game_stage == 2: 
            direction = lane_vel
            speed = 40
            gear = 1
            if traffic_light_data == 3:  # 禁速
                speed = 11
            if traffic_light_data == 4:  # 解禁速
                speed = 40
            if traffic_light_data == 7:
                speed = 21
            if traffic_light_data == 8:  # 停止
                speed = 0
                gear = 0
                game_stage = 3
        if game_stage == 3:
            if motorspeed == 0:
                game_stage == 4
        if game_stage == 4:
            direction = lane_vel
            speed = 40 
            gear = 1
            if traffic_light_data == 2:  # 黄灯
                speed = 0
                gear = 0
                direction = 50
                game_stage = 0
        print(game_stage)
        # speed = 40
        # gear = 1
        # direction = lane_vel

        if lidobj == 1:
            speed = 0
            gear = 0
        pub1.publish(manul)
        pub2.publish(direction)
        pub3.publish(speed)
        pub4.publish(gear)
        rate.sleep()

if __name__ == '__main__':
    kinematicCtrl()

