from socket import *
from threading import Thread


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

# def socketSendMsg(socketObj, labelName):
#     try:
#         connection, address = socketObj.accept() # Socket ACCept
#         connection.send(labelName.encode("utf-8")) #Socket Send
#         print("Sent: ",  labelName)
#         connection.close
#     except:
#         pass

def socketencode(labelname):  # 编码协议
    data = '404'
    if labelname == []:
        data = '404'  # 未检测到
    else:
        if 0 in labelname:
            data = "0"  # speed limit
        if 1 in labelname:
            data = "1"  # 绿灯
        if 2 in labelname:
            data = "2"  # 人行道
        if 3 in labelname:
            data = "3"  # 红灯
        if 4 in labelname:
            data = "4"  # 禁速
    return data