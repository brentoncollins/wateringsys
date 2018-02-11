#!/usr/bin/python
#!/

import RPi.GPIO as GPIO
import time
import MySQLdb as my
import sys

cursor = db.cursor()
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)                                # set gpio pin 24 to an output as to turn the pump on when needed
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)     # set gpio pin 23 as an inpuut to monitor if the water level is sufficent 

pumpcommand = str(sys.argv[1])

start = "start"
stop = "stop"

def pumprun():
		# Manual pump run script the the user interface.
	try:
		if  GPIO.input(23)==1:	
			if  pumpcommand == start:
				GPIO.output (24 ,1)
				GPIO.output (4 ,1)

		if  pumpcommand == stop:
				GPIO.output (24 ,0)
				GPIO.output (4 ,0)
		
		if  GPIO.input(23)== 0:
			print "\nWater level is low, pump will not run\n"

	except Exception as e:
		print(e)
		GPIO.cleanup() 
		GPIO.output (24 , 0)

pumprun()

	





