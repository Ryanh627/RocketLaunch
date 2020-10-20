

import RPi.GPIO as GPIO
from pad import *
GPIO.setmode(GPIO.BOARD)

if (pad.pinIn == 13){
GPIO.setup(37,GPIO.OUT) 
GPIO.output(37,GPIO.HIGH) 
GPIO.output(37,GPIO.LOW)
time.sleep(1)
GPIO.output(37,GPIO.HIGH) 
print "Launched Pad1"
}
if (pad.pinIn == 15){
GPIO.setup(38,GPIO.OUT) 
GPIO.output(38,GPIO.HIGH) 
GPIO.output(38,GPIO.LOW)
time.sleep(1)
GPIO.output(38,GPIO.HIGH) 
print "Launched Pad2"}

if (pad.pinIn == 23){
GPIO.setup(40,GPIO.OUT) 
GPIO.output(40,GPIO.HIGH) 
GPIO.output(40,GPIO.LOW)
time.sleep(1)
GPIO.output(40,GPIO.HIGH)
print "Launched Pad3" }



