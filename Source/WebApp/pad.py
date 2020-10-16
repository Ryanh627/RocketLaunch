import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)




class Pad:
    #Constructor
    def __init__(self, name, pinIn, pinOut):
        self.pinIn = pinIn
        self.pinOut = pinOut
        self.connected = False
        self.name = name

    #Update connection field by checking physical rocket port connection
    def check_connection(self):
	GPIOpin = self.pinIn
	GPIO.setup(GPIOpin, GPIO.In, pull_up_down=GPIO.PUD_UP)

	state = GPIO.input(GPIOpin)
	if state == False:
		self.connected = True
	else:
		self.connected = False

	GPIO.cleanup(GPIOpin)

    def launch(self):
        print("Launched " + self.name)

#Construct a list of pad objects from the pad configuration file
def pads_setup():
    #Create empty list and open pad configuration file
    pads = []
    stream = open('/home/pi/RocketLaunch/Source/WebApp/pad.conf', 'r')

    #Skip first line, read all lines into a list, initialize index
    next(stream)
    lines = stream.readlines()
    i = 1
    
    #For every line
    for line in lines:

        #Get rid of newline at end, split by tab character into a list
        line = line[2:].strip("\n")
        args = line.split('\t')

        #Create pad object, add to list, iterate index
        pad = Pad('Pad ' + str(i), args[0], args[1])
        pads.append(pad)
        i = i + 1
    
    #Close the file
    stream.close()

    #Return the pad list
    return pads
