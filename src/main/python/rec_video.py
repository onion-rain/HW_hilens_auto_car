import cv2
import hilens
# import os
# import requests


def rec_video(cap, display, show):
    # if not os.path.exists("video/"):
    #     os.makedirs("video/")
    fps = 20
    size = (1280, 720)
    format = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
    writer = cv2.VideoWriter("/tmp/test.avi", format, fps, size)
    frame_num = fps*20
    for ix in range(frame_num):
        image = cap.read()
        img_bgr = cv2.cvtColor(image, cv2.COLOR_YUV2BGR_NV21)
        writer.write(img_bgr)
        if show:
            display.show(image)  # 显示到屏幕上
    writer.release()
    # hilens.upload_file("video", hilens.get_workspace_path()+"test.avi", "write")

    # print("start upload")
    # error_code = hilens.upload_file("huaji.jpg", hilens.get_workspace_path()+"smallhuaji.jpg", "write")
    # print(error_code)
    # print("end upload")

