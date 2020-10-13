from picamera import PiCamera#imports for using Pi Camera
from time import sleep

camera = PiCamera() #sets up the camera
camera.resolution = (1920, 1080)#resolution settings
camera.framerate = 30 #framerate settings
#OTHER RESOLUTIONS AND FRAMERATES SUPPORTED BY PI CAMERA V2:
#
#camera.resolution = (1280, 720)
#camera.framerate = 60
#
#camera.resolution = (640, 480)
#camera.framerate = 90


camera.start_preview() #starts onscreen preview of camera
camera.start_recording('/home/pi/Desktop/video2.h264') #Starts recording of camera
sleep(5)#waits for 5 seconds which is how long the camera will record for
camera.stop_recording() #stops recording
camera.stop_preview()#stops preview