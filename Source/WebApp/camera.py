#Developed and owned by Benjamin Eckert, Peter Gifford, and Ryan Hansen of Western Michigan University.

#camera.py controls the functionality of the camera wired to the pi

import picamera
from database import *
from subprocess import call
from datetime import *
from time import *

def take_video(users):
    try:
        camera = picamera.PiCamera()
        location = "/home/pi/RocketLaunch/Source/WebApp/static/media/videos/"
        videoname = "tempclip.h264"
        File_h264 = videoname

        today = date.today()
        fdate = today.strftime("%b-%d-%Y:")
        time = datetime.now()

        ftime = time.strftime("%H:%M:%S")
        File_mp4 = "clip_" + fdate+ftime+".mp4"
        
        command = "MP4Box -add " + location+File_h264 + " " + location+File_mp4

        duration = db_get_setting("RECORDINGDURATION")
        
        camera.start_recording(location+videoname)
        camera.wait_recording(duration)
        camera.stop_recording()
        camera.close()

        call([command], shell = True)

        user_list = []

        for user in users:
            if user != 'None':
                user_list.append(user)

        if(len(user_list) != 0):
            db_insert_video(user_list, File_mp4)

    except Exception as e:
        print(e)
