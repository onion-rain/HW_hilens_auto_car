import cv2
# import hilens
import os
# import requests


def rec_video(cap, display, show):
    if not os.path.exists("/tmp/"):
        os.makedirs("/tmp/")
    length = 20  # s
    fps = 24
    size = (1280, 720)
    format = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
    frame_num = fps*length
    i = 0
    while(1):
        writer = cv2.VideoWriter("/tmp/test{}.avi".format(i), format, fps, size)
        for ix in range(frame_num):
            image = cap.read()
            img_bgr = cv2.cvtColor(image, cv2.COLOR_YUV2BGR_NV21)
            writer.write(img_bgr)
            if show:
                display.show(image)  # 显示到屏幕上
        writer.release()
        i += 1
    # hilens.upload_file("video", hilens.get_workspace_path()+"test.avi", "write")

    # print("start upload")
    # error_code = hilens.upload_file("huaji.jpg", hilens.get_workspace_path()+"smallhuaji.jpg", "write")
    # print(error_code)
    # print("end upload")

