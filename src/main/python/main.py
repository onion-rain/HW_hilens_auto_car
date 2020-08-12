# -*- coding: utf-8 -*-
# !/usr/bin/python3
# SkillFramework 0.2.2 python demo

import os
import cv2
import time
import hilens
from utils import preprocess
from utils import preprocess_with_pad
from utils import get_result
from utils import get_result_with_pad
from utils import draw_boxes
from utils import convert_to_json
from utils import save_json_to_file
from utils import label_transform

pad = 0
rgb = 0

def run(work_path):
    # 系统初始化，参数要与创建技能时填写的检验值保持一致
    hilens.init("driving")

    # 初始化自带摄像头与HDMI显示器,
    # hilens studio中VideoCapture如果不填写参数，则默认读取test/camera0.mp4文件，
    # 在hilens kit中不填写参数则读取本地摄像头
    camera = hilens.VideoCapture()
    display = hilens.Display(hilens.HDMI)

    # 初始化模型
# -*- coding: utf-8 -*-
    # model_path = os.path.join(work_path, 'model/driving_model.om')
    # model_path = os.path.join(work_path, 'model/yolo3_darknet53_raw0_0_terminal_t.om')
    # model_path = os.path.join(work_path, 'model/yolo3_darknet53_raw0_1_terminal_t.om')
    # model_path = os.path.join(work_path, 'model/yolo3_darknet53_raw1_rvh_terminal_t.om')
    # model_path = os.path.join(work_path, 'model/yolo3_darknet53_raw1_rvhm_terminal_t.om')
    # model_path = os.path.join(work_path, 'model/yolo3_darknet53_raw1_terminal_t.om')
    # model_path = os.path.join(work_path, 'model/yolo3_darknet53_raw2_terminal_t.om')
    # model_path = os.path.join(work_path, 'model/yolo3_darknet53_raw3_terminal_t.om')
    model_path = os.path.join(work_path, 'model/yolo3_darknet53_raw3_rvhm_terminal_t.om')
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
            img_bgr = cv2.cvtColor(
                input_yuv, cv2.COLOR_YUV2BGR_NV21)  # 转为BGR格式

            if rgb:
                img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            else:
                img_rgb = img_bgr


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


            bboxes = label_transform(bboxes)

            # 5-1. [比赛提交作品用] 将结果输出到json文件中 #####
            if len(bboxes) > 0:
                json_bbox = convert_to_json(bboxes, frame_index)
                json_bbox_list.append(json_bbox)

            # 5-2. [调试用] 将结果输出到模拟器中 #####

            if rgb:
                img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
            else:
                img_bgr = img_rgb
            

            img_bgr = draw_boxes(img_bgr, bboxes)  # 在图像上画框
            output_yuv = hilens.cvt_color(img_bgr, hilens.BGR2YUV_NV21)
            display.show(output_yuv)  # 显示到屏幕上
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


if __name__ == "__main__":
    run(os.getcwd())
