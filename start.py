import os
import uuid
import sys
sys.path.append("./src/main/python")
import main

try:
    work_path = os.getcwd()
    random_number = str(uuid.uuid1())
    with open(os.path.join(work_path, '.hilens/rtmp.txt'), 'w') as f:
        f.write(random_number)

    os.environ['RTMP_PATH'] = "rtmp://127.0.0.1/live/" + random_number
    #os.chdir('src/main/python/')
    main.run(work_path)
finally:
    with open(os.path.join(work_path, '.hilens/rtmp.txt'), 'r+') as f:
        f.truncate()
