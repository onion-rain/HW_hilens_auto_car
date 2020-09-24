from socket import socket, AF_INET, SOCK_STREAM
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


def data_generate_4(bbox):
    class_names = ["center_wall", "green_go", "red_stop",
                   "sidewalk", 'slope', "speed_limit", "speed_unlimit", "yellow_back"]
    send_data = 0
    data = 0
    if bbox == []:
        data = 'zzz'
        return data

    label_names = [class_names[i[4]] for i in bbox]
    label_attr = []
    for i in range(len(label_names)):
        label_name = label_names[i]
        if label_name in ['sidewalk', 'speed_limit', 'speed_unlimit', 'slope', 'red_stop']:
            label_attr.append((bbox[i][:4]))  # 如果检测到人行道，限速，解禁速，返回xyxy
        else:
            label_attr.append((bbox[i][0]+bbox[i][2])/2)  # 当前版本如果检测到其他，返回检测物体的x中心
    data = dict(zip(label_names, label_attr))  # 形成一个信息字典，e.g {'green_go':255, 'sidewalk':750}
    send_data = json.dumps(data)

    return send_data
