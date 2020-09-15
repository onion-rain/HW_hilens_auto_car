from socket import *
import json
# def socket_init():
#     # 设置socket通信
#     HOST = '192.168.2.111'
#     PORT = 7777
#     # bufsize = 1024
#     socket_3399 = socket(AF_INET, SOCK_STREAM)
#     socket_3399.bind((HOST, PORT))
#     socket_3399.listen()
#     connection, _ = socket_3399.accept()  # Socket ACCept
#     print("accepted")
#     return connection


def socket_init():
    # 设置socket通信
    HOST = '192.168.2.111'
    PORT = 7777
    # bufsize = 1024
    socket_3399 = socket(AF_INET, SOCK_STREAM)
    socket_3399.bind((HOST, PORT))
    return socket_3399


def socketSendMsg(connection, labelName):
    if labelName == []:
        labelName = [0]
    print("Sent: ",  labelName)
    try:
        connection.send(labelName.encode("utf-8"))  # Socket Send
    except:
        pass


def socketencode(labelname):  # 编码协议
    data = '404'
    if labelname == []:
        data = '404'  # 未检测到
    else:
        if 0 in labelname:
            data = "0"  # wall
        if 1 in labelname:
            data = "1"  # 绿灯
        if 2 in labelname:
            data = "2"  # 红灯
        if 3 in labelname:
            data = "3"  # 人行道
        if 4 in labelname:
            data = "4"  # 禁速
        if 5 in labelname:
            data = "5"  # 解禁速
        if 6 in labelname:
            data = "6"  # 黄灯
    return data


def socket_accept(socket_obj, labelname):
    connection, _ = socket_obj.accept()
    data = socketencode(labelname)
    socketSendMsg(connection, data)

    return connection


def data_generate(bbox):
    # class_names = ["center_wall", "green_go", "red_stop",
    #                "sidewalk", "speed_limit", "speed_unlimit", "yellow_back"]
    label_name = [i[4] for i in bbox]
    if bbox == []:
        data = '404'
    else:
        data = socketencode(label_name)
    if data == '3':
        side_index = label_name.index(3)
        side_attr = str(bbox[side_index][1])+','+str(bbox[side_index][3])
        data = '3,' + side_attr
    return data


def data_generate_2(bbox):
    class_names = ["center_wall", "green_go", "red_stop",
                   "sidewalk", "speed_limit", "speed_unlimit", "yellow_back"]
    if bbox == []:
        data = '404'
    else:
        label_name = [class_names[i[4]] for i in bbox]
        label_attr = []
        for i in range(len(label_name)):
            if label_name == 'sidewalk':
                label_attr.append((bbox[i][1]))  # 如果检测到人行道，返回人行道的ymin
            elif label_name == 'speed_limit':
                label_attr.appedn((bbox[i][1]))  # 如果检测到限速牌，返回限速牌的ymin
            else:
                label_attr.append((bbox[i][2]+bbox[i][0])/2)  # 当前版本如果检测到其他，返回检测物体的中心
        data = dict(zip(label_name, label_attr))  # 形成一个信息字典，e.g {'green_go':255, 'sidewalk':750}

    if 'green_go' in data:
        send_data = 'go'
    elif 'red_stop' in data:
        send_data = 'stop'
    elif 'yellow_back' in data:
        send_data = 'yellow'
    if 'sidewalk' in data and data['sidewalk'] < 680:
        send_data = 'stop'

    # 限速牌的控制
    if 'speed_limit' in data and data['speed_limit'] < 480:
        send_data = 'slow'
    elif 'speed_unlimit' in data and data['speed_unlimit'] < 480:
        send_data = 'quick'

    if data == '404':
        send_data = 'continue'

    return send_data
