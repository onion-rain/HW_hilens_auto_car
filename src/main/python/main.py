# -*- coding: utf-8 -*-
# !/usr/bin/python3
# SkillFramework 0.2.2 python demo

import argparse
import os
import cv2
import time
import hilens

from utils import preprocess
from utils import preprocess_with_pad
from utils import get_result
from utils import get_result_with_pad
from utils import draw_boxes
from utils import save_json_to_file

from rec_video import rec_video
from socket_config import socket_init
from socket_config import socketSendMsg
from socket_config import data_generate_4
import threading


parser = argparse.ArgumentParser(description='auto car')
parser.add_argument('--pad', action='store_true')
parser.add_argument('--rgb', action='store_true')
parser.add_argument('--show', action='store_true')
parser.add_argument('--log', action='store_true')
parser.add_argument('--rec', action='store_true')
parser.add_argument('--socket', action='store_true')
args = parser.parse_args()

print(args)

pad = args.pad
rgb = 1
show = args.show
log = args.log
rec = args.rec
socket_use = args.socket

# pad = 1
# rgb = 1
show = 1
log = 1
socket_use = 1
# rec = 1

data = '404'  # 线程间共享参数


def run(work_path):

    global data

    # 系统初始化，参数要与创建技能时填写的检验值保持一致
    hilens.init("driving")

    # 初始化自带摄像头与HDMI显示器,
    # hilens studio中VideoCapture如果不填写参数，则默认读取test/camera0.mp4文件，
    # 在hilens kit中不填写参数则读取本地摄像头
    camera = hilens.VideoCapture()
    # camera = hilens.VideoCapture("test/new.mp4")

    display = hilens.Display(hilens.HDMI)

    if rec:
        rec_video(camera, display, show)

    # 初始化模型
    # -*- coding: utf-8 -*-
    # model_path = os.path.join(work_path, 'model/yolo3_darknet53_new_raw3_4_terminal_t.om')
    # model_path = os.path.join(work_path, 'model/yolo3_darknet53_new_raw3_rm_terminal_t.om')
    model_path = os.path.join(work_path, 'model/yolo3_darknet53_new_raw3_terminal_t.om')

    driving_model = hilens.Model(model_path)

    frame_index = 0
    json_bbox_list = []
    json_data = {'info': 'det_result'}

    while True:
        frame_index += 1
        try:
            time_start = time.time()

            # 1. 设备接入 #####
            input_yuv = camera.read()  # 读取一帧图片(YUV NV21格式)

            # 2. 数据预处理 #####
            if rgb:
                img_rgb = cv2.cvtColor(input_yuv, cv2.COLOR_YUV2RGB_NV21)  # 转为RGB格式
            else:
                img_rgb = cv2.cvtColor(input_yuv, cv2.COLOR_YUV2BGR_NV21)  # 转为BGR格式

            if pad:
                img_preprocess, img_w, img_h, new_w, new_h, shift_x_ratio, shift_y_ratio = preprocess_with_pad(img_rgb)  # 缩放为模型输入尺寸
                # 3. 模型推理 #####
                output = driving_model.infer([img_preprocess.flatten()])
                # 4. 获取检测结果 #####
                bboxes = get_result_with_pad(output, img_w, img_h, new_w, new_h, shift_x_ratio, shift_y_ratio)
            else:
                img_preprocess, img_w, img_h = preprocess(img_rgb)  # 缩放为模型输入尺寸
                # 3. 模型推理 #####
                output = driving_model.infer([img_preprocess.flatten()])
                # 4. 获取检测结果 #####
                bboxes = get_result(output, img_w, img_h)

            # # 5-1. [比赛提交作品用] 将结果输出到json文件中 #####
            # if len(bboxes) > 0:
            #     json_bbox = convert_to_json(bboxes, frame_index)
            #     json_bbox_list.append(json_bbox)
            # # if bboxes != []:
            # #     print()

            if socket_use:
                data = data_generate_4(bboxes)

            # 5-2. [调试用] 将结果输出到display #####
            if show:
                if rgb:
                    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
                else:
                    img_bgr = img_rgb
                img_bgr, labelName = draw_boxes(img_bgr, bboxes)  # 在图像上画框
                output_yuv = hilens.cvt_color(img_bgr, hilens.BGR2YUV_NV21)
                display.show(output_yuv)  # 显示到屏幕上
            if log:
                time_frame = 1000 * (time.time() - time_start)
                hilens.info('----- time_frame = %.2fms -----' % time_frame)

        except RuntimeError:
            print('last frame')
            break

    # 保存检测结果
    hilens.info('write json result to file')
    result_filename = './result.json'
    json_data['result'] = json_bbox_list
    save_json_to_file(json_data, result_filename)
    hilens.terminate()


def socket_run():  # 修改了socket_accept函数
    global labelname
    global data
    connection = 0
    socket_3399 = socket_init()
    socket_3399.listen()  # Socket ACCept
    connection, _ = socket_3399.accept()
    socketSendMsg(connection, data)
    # connection = socket_accept(socket_3399, labelname)
    while True:
        try:
            connection.recv(1024)
            # data = socketencode(labelname)
            socketSendMsg(connection, data)
        except ConnectionResetError:
            # connection = socket_accept(socket_3399, labelname)
            socket_3399.listen()
            connection, _ = socket_3399.accept()
            socketSendMsg(connection, data)


def my_main():
    # thread1 = threading.Thread(target=run, args=(os.getcwd(), ))
    # thread1.start()
    if socket_use:
        thread2 = threading.Thread(target=socket_run)
        thread2.start()
    run(os.getcwd())


if __name__ == "__main__":
    my_main()
