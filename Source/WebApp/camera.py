import picamera
import configparser
from time import sleep

def take_video():
    
    config = configparser.ConfigParser()
    config.read('launch_settings.conf')
    
    if config.getboolean('doVideo'):
        
        camera = picamera.PiCamera()
        location = "/home/pi/RocketLaunch/Source/WebApp/static/media/Clips"
        videoname = "clip{counter:02d}.h264"
        duration = config.getint('duration')
        
        camera.start_recording(location+videoname)
        camera.wait_recording(duration)
        camera.stop_recording()
        camera.close()
<<<<<<< HEAD:Source/WebApp/Camera.py
        
        
=======
>>>>>>> 1c6a864620d5d8e416b2442591971d9c4c146512:Source/WebApp/camera.py
