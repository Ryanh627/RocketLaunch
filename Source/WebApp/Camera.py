import picamera
from time import sleep

def take_video():
    camera = picamera.PiCamera()
    
    location = "/home/pi/RocketLaunch/Source/WebApp/static/media/Clips"
    videoname = "clip{counter:02d}.h264"
    duration = 5
    camera.start_recording(location+videoname)
    camera.wait_recording(duration)
    camera.stop_recording()
    camera.close()