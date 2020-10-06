import RPi.GPIO as GPIO
import time
from time import sleep
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


while True:
	print('Closed Circuit')
	sleep(10)


