#Developed and owned by Benjamin Eckert, Peter Gifford, and Ryan Hansen of Western Michigan University.

#camera.py controls the functionality of the camera wired to the pi

import picamera
from database import *
from subprocess import call
from datetime import *
import time

def take_video():
    
    if db_get_setting("RECORDLAUNCH"):
        
        camera = picamera.PiCamera()
        location = "/home/pi/RocketLaunch/Source/WebApp/static/media/Clips/"
        videoname = "tempclip.h264"
        File_h264 = location+videoname
        
        today = date.today()
        fdate = today.strftime("%b-%d-%Y:")
        
        time = datetime.now()
        ftime = time.strftime("%H:%M:%S")
        File_mp4 = location + "clip_" + fdate+ftime+".mp4"
        
        command = "MP4Box -add " + File_h264 + " " + File_mp4
        
        duration = db_get_setting("RECORDINGDURATION")
        
        camera.start_recording(location+videoname)
        camera.wait_recording(duration)
        camera.stop_recording()
        camera.close()
        
        call([command], shell = True)
        
        users = db_get_authorized_users()
        if(len(users) == 0):
            users = ["None", "None", "None"]
            
        db_insert_video(users, File_mp4)
