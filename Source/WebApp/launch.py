

import RPi.GPIO as GPIO
from pad import *
GPIO.setmode(GPIO.BOARD)

if (pad.name == 1){
GPIO.setup(37,GPIO.OUT) 
GPIO.output(37,GPIO.HIGH) 
GPIO.output(37,GPIO.LOW)
time.sleep(1)
GPIO.output(37,GPIO.HIGH) 
print "Launched Pad1"
}
if (pad.name == 2){
GPIO.setup(38,GPIO.OUT) 
GPIO.output(38,GPIO.HIGH) 
GPIO.output(38,GPIO.LOW)
time.sleep(1)
GPIO.output(38,GPIO.HIGH) 
print "Launched Pad2"}

if (pad.name == 3){
GPIO.setup(40,GPIO.OUT) 
GPIO.output(40,GPIO.HIGH) 
GPIO.output(40,GPIO.LOW)
time.sleep(1)
GPIO.output(40,GPIO.HIGH)
print "Launched Pad3" }



