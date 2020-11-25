#Developed and owned by Benjamin Eckert, Peter Gifford, and Ryan Hansen of Western Michigan University.

#camera.py controls the functionality of the camera wired to the pi

import picamera
from database import *
from subprocess import call
from datetime import date
import time

def take_video():
    
    if db_get_setting("RECORDLAUNCH"):
        
        camera = picamera.PiCamera()
        location = "/home/pi/RocketLaunch/Source/WebApp/static/media/Clips/"
        videoname = "tempclip.h264"
        File_h264 = location+videoname
        date = fdate = date.today().strftime('%d/%m/%Y')
        time = time.strftime("%H:%M:%S")
        
        command = "MP4Box -add " + location+videoname + " " + location + "clip"+date+ ":" + time + ".mp4"
        
        duration = db_get_setting("RECORDINGDURATION")
        
        camera.start_recording(location+videoname)
        camera.wait_recording(duration)
        camera.stop_recording()
        camera.close()
        
        call([command], shell = True)
        
        #db_insert_video(users, location + "clip.mp4")
