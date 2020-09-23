# -*- coding: utf-8 -*-
# !/usr/bin/python3
# utils for traffic sign detection

import cv2
import json
import numpy as np

# 测试视频尺寸(368, 640, 3)
# hilens kit(720, 1280, 3)

# 模型输入尺寸
net_h = 416
net_w = 416

# class_names = ["slope"]
class_names = ["wall", "green", "red", "sidewalk", "slope", "limit", "unlimit", "yellow"]
class_thres = [0.6,    0.7,     0.7,   0.4,        0.3,     0.4,     0.7,       0.3]
class_num = len(class_names)

# 检测框的输出阈值、NMS筛选阈值
conf_threshold = 0.3  # 所有分类最低conf
iou_threshold = 0.4

# 检测模型的anchors，用于解码出检测框
stride_list = [8, 16, 32]
anchors_1 = np.array([[10, 13],   [16, 30],   [33, 23]]) / stride_list[0]
anchors_2 = np.array([[30, 61], [62, 45],   [59, 119]]) / stride_list[1]
anchors_3 = np.array([[116, 90], [156, 198], [163, 326]]) / stride_list[2]
anchor_list = [anchors_1, anchors_2, anchors_3]

colors = [(127, 127, 127), (0, 255, 0), (0, 0, 255),
          (255, 255, 0), (255, 255, 255), (255, 0, 255), (255, 0, 0), (0, 255, 255)]


# 图片预处理：缩放到模型输入尺寸
def preprocess(img_data):
    h, w, c = img_data.shape
    new_image = cv2.resize(img_data, (net_w, net_h))
    return new_image, w, h


def preprocess_with_pad(image, aipp_flag=True):
    img_h, img_w, img_c = image.shape

    scale = min(float(net_w) / float(img_w), float(net_h) / float(img_h))
    new_w = int(img_w * scale)
    new_h = int(img_h * scale)

    shift_x = (net_w - new_w) // 2
    shift_y = (net_h - new_h) // 2
    shift_x_ratio = (net_w - new_w) / 2.0 / net_w
    shift_y_ratio = (net_h - new_h) / 2.0 / net_h

    image_ = cv2.resize(image, (new_w, new_h))

    if aipp_flag:
        new_image = np.zeros((net_h, net_w, 3), np.uint8)
    else:
        new_image = np.zeros((net_h, net_w, 3), np.float32)
    new_image.fill(128)

    new_image[shift_y: new_h + shift_y, shift_x: new_w + shift_x, :] = np.array(image_)

    if not aipp_flag:
        new_image /= 255.

    return new_image, img_w, img_h, new_w, new_h, shift_x_ratio, shift_y_ratio


def overlap(x1, x2, x3, x4):
    left = max(x1, x3)
    right = min(x2, x4)
    return right - left


# 计算两个矩形框的IOU
def cal_iou(box1, box2):
    w = overlap(box1[0], box1[2], box2[0], box2[2])
    h = overlap(box1[1], box1[3], box2[1], box2[3])
    if w <= 0 or h <= 0:
        return 0
    inter_area = w * h
    union_area = (box1[2] - box1[0]) * (box1[3] - box1[1]) + \
                 (box2[2] - box2[0]) * (box2[3] - box2[1]) - inter_area
    return inter_area * 1.0 / union_area


# 使用NMS筛选检测框
def apply_nms(all_boxes, iou_thres, cls_thres):
    res = []

    for cls in range(class_num):
        cls_bboxes = all_boxes[cls]
        cls = cls+1 if cls+1 < 7 else 0
        if cls_bboxes == []:
            continue
        # else:
        #     if cls == 0:
        #         pass
        #     elif cls == 1:
        #         pass
        #     elif cls == 2:
        #         pass
        #     elif cls == 3:
        #         pass
        #     elif cls == 4:
        #         pass
        #     elif cls == 5:
        #         pass
        #     elif cls == 6:
        #         pass
        conf_thres = cls_thres[cls]
        keep_boxes = [box for box in cls_bboxes if box[-1] > conf_thres]
        if len(keep_boxes) < len(cls_bboxes):
            print()
        sorted_boxes = sorted(keep_boxes, key=lambda d: d[5])[::-1]
        p = dict()
        for i in range(len(sorted_boxes)):
            if i in p:
                continue

            truth = sorted_boxes[i]
            for j in range(i+1, len(sorted_boxes)):
                if j in p:
                    continue
                box = sorted_boxes[j]
                iou = cal_iou(box, truth)
                if iou >= iou_thres:
                    p[j] = 1

        for i in range(len(sorted_boxes)):
            if i not in p:
                res.append(sorted_boxes[i])
    return res


# 从模型输出的特征矩阵中解码出检测框的位置、类别、置信度等信息
def decode_bbox(conv_output, anchors, img_w, img_h):

    def _sigmoid(x):
        s = 1 / (1 + np.exp(-x))
        return s

    _, h, w = conv_output.shape
    pred = conv_output.transpose((1, 2, 0)).reshape((h * w, 3, 5+class_num))

    pred[..., 4:] = _sigmoid(pred[..., 4:])
    pred[..., 0] = (_sigmoid(pred[..., 0]) +
                    np.tile(range(w), (3, h)).transpose((1, 0))) / w
    pred[..., 1] = (_sigmoid(pred[..., 1]) +
                    np.tile(np.repeat(range(h), w), (3, 1)).transpose((1, 0))) / h
    pred[..., 2] = np.exp(pred[..., 2]) * anchors[:, 0:1].transpose((1, 0)) / w
    pred[..., 3] = np.exp(pred[..., 3]) * anchors[:, 1:2].transpose((1, 0)) / h

    bbox = np.zeros((h * w, 3, 4))
    bbox[..., 0] = np.maximum((pred[..., 0] - pred[..., 2] / 2.0) * img_w, 0)     # x_min
    bbox[..., 1] = np.maximum((pred[..., 1] - pred[..., 3] / 2.0) * img_h, 0)     # y_min
    bbox[..., 2] = np.minimum((pred[..., 0] + pred[..., 2] / 2.0) * img_w, img_w)  # x_max
    bbox[..., 3] = np.minimum((pred[..., 1] + pred[..., 3] / 2.0) * img_h, img_h)  # y_max

    pred[..., :4] = bbox
    pred = pred.reshape((-1, 5+class_num))
    pred[:, 4] = pred[:, 4] * pred[:, 5:].max(1)    # 类别
    pred = pred[pred[:, 4] >= conf_threshold]
    pred[:, 5] = np.argmax(pred[:, 5:], axis=-1)    # 置信度

    all_boxes = [[] for ix in range(class_num)]
    for ix in range(pred.shape[0]):
        box = [int(pred[ix, iy]) for iy in range(4)]
        box.append(int(pred[ix, 5]))
        box.append(pred[ix, 4])
        all_boxes[box[4]-1].append(box)

    return all_boxes


def decode_bbox_with_pad(conv_output, anchors, img_w, img_h, x_scale, y_scale, shift_x_ratio, shift_y_ratio):
    def _sigmoid(x):
        s = 1 / (1 + np.exp(-x))
        return s

    _, h, w = conv_output.shape
    pred = conv_output.transpose((1, 2, 0)).reshape((h * w, 3, 5 + class_num))

    pred[..., 4:] = _sigmoid(pred[..., 4:])
    pred[..., 0] = (_sigmoid(pred[..., 0]) + np.tile(range(w), (3, h)).transpose((1, 0))) / w
    pred[..., 1] = (_sigmoid(pred[..., 1]) + np.tile(np.repeat(range(h), w), (3, 1)).transpose((1, 0))) / h
    pred[..., 2] = np.exp(pred[..., 2]) * anchors[:, 0:1].transpose((1, 0)) / w
    pred[..., 3] = np.exp(pred[..., 3]) * anchors[:, 1:2].transpose((1, 0)) / h

    bbox = np.zeros((h * w, 3, 4))
    bbox[..., 0] = np.maximum((pred[..., 0] - pred[..., 2] / 2.0 - shift_x_ratio) * x_scale * img_w, 0)  # x_min
    bbox[..., 1] = np.maximum((pred[..., 1] - pred[..., 3] / 2.0 - shift_y_ratio) * y_scale * img_h, 0)  # y_min
    bbox[..., 2] = np.minimum((pred[..., 0] + pred[..., 2] / 2.0 - shift_x_ratio) * x_scale * img_w, img_w)  # x_max
    bbox[..., 3] = np.minimum((pred[..., 1] + pred[..., 3] / 2.0 - shift_y_ratio) * y_scale * img_h, img_h)  # y_max

    pred[..., :4] = bbox
    pred = pred.reshape((-1, 5 + class_num))
    pred[:, 4] = pred[:, 4] * pred[:, 5:].max(1)
    pred = pred[pred[:, 4] >= conf_threshold]
    pred[:, 5] = np.argmax(pred[:, 5:], axis=-1)

    return pred

    all_boxes = [[] for ix in range(class_num)]
    for ix in range(pred.shape[0]):
        box = [int(pred[ix, iy]) for iy in range(4)]
        box.append(int(pred[ix, 5]))
        box.append(pred[ix, 4])
        all_boxes[box[4] - 1].append(box)

    return all_boxes


# 从模型输出中得到检测框
def get_result(model_outputs, img_w, img_h):

    num_channel = 3 * (class_num + 5)
    all_boxes = [[] for ix in range(class_num)]
    for ix in range(3):
        pred = model_outputs[2-ix].reshape(
            (num_channel, net_h // stride_list[ix], net_w // stride_list[ix]))
        anchors = anchor_list[ix]
        boxes = decode_bbox(pred, anchors, img_w, img_h)
        all_boxes = [all_boxes[iy] + boxes[iy] for iy in range(class_num)]

    res = apply_nms(all_boxes, iou_threshold, class_thres)
    return res


def get_result_with_pad(model_outputs, img_w, img_h, new_w, new_h, shift_x_ratio, shift_y_ratio):
    num_channel = 3 * (class_num + 5)
    x_scale = net_w / float(new_w)
    y_scale = net_h / float(new_h)
    all_boxes = [[] for ix in range(class_num)]
    for ix in range(3):
        pred = model_outputs[2 - ix].reshape(
            (num_channel, net_h // stride_list[ix], net_w // stride_list[ix]))
        anchors = anchor_list[ix]
        boxes = decode_bbox_with_pad(pred, anchors, img_w, img_h, x_scale, y_scale, shift_x_ratio, shift_y_ratio)
        all_boxes = [all_boxes[iy] + boxes[iy] for iy in range(class_num)]

    res = apply_nms(all_boxes, iou_threshold)
    return res


def convert_to_json(bboxes, frame_index):
    json_bbox = {'frame_id': frame_index}
    bbox_list = []
    for bbox in bboxes:
        bbox_info = {}
        bbox_info['x_min'] = int(bbox[0])
        bbox_info['y_min'] = int(bbox[1])
        bbox_info['x_max'] = int(bbox[2])
        bbox_info['y_max'] = int(bbox[3])
        bbox_info['label'] = int(bbox[4])
        bbox_info['score'] = int(bbox[5] * 100)
        bbox_list.append(bbox_info)
    json_bbox['bboxes'] = bbox_list
    return json_bbox


def save_json_to_file(json_data, result_filename):
    with open(result_filename, 'w') as f:
        json.dump(json_data, f)


# 在图中画出检测框，输出类别信息 
# 新增加了功能，返回标签名
def draw_boxes(img_data, bboxes):
    thickness = 2
    font_scale = 1
    text_font = cv2.FONT_HERSHEY_SIMPLEX
    labelName = ""
    for bbox in bboxes:
        label = int(bbox[4])
        conf = float(bbox[5])
        x_min = int(bbox[0])
        y_min = int(bbox[1])
        x_max = int(bbox[2])
        y_max = int(bbox[3])
        cv2.rectangle(img_data, (x_min, y_min),
                      (x_max, y_max), colors[label], thickness)
        cv2.putText(img_data, "{:.2f},{:.2f}".format(x_min, x_max), (x_min, y_min-50),
                    text_font, font_scale, colors[label], thickness)
        cv2.putText(img_data, "{:.2f},{:.2f}".format(y_min, y_max), (x_min, y_min-25),
                    text_font, font_scale, colors[label], thickness)
        cv2.putText(img_data, class_names[label]+"_{:.2f},{:.2f}".format(conf, (x_min + x_max)/2), (x_min, y_min),
                    text_font, font_scale, colors[label], thickness)
        labelName = class_names[label]

    return img_data, labelName


# def bboxes_limit(prediction, cls, num=1):
#     """指定cls保留num个预测框, inplace操作
#     args:
#         prediction[batch, (x, y, x, y, object_confidence, class_score, class_pred)]
#         cls: 类别
#         num：bbox保留个数
#     """
#     for idx in range(len(prediction)):
#         p = prediction[idx]
#         if p is None:
#             continue
#         cls_ids = torch.where(p[:, -1] == cls)[0]
#         othercls_ids = torch.where(p[:, -1] != cls)[0]
#         if len(cls_ids) <= num:
#             continue
#         ids = torch.sort(p[cls_ids][:, 4]+p[cls_ids][:, 5], 0, )[1]
#         keepcls_ids = cls_ids[ids[:num]]
#         keep_ids = torch.cat((keepcls_ids, othercls_ids), 0)
#         prediction[idx] = p[keep_ids]
