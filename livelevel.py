#!/usr/bin/python3
#!/

# This is a python script reading the live level in the water tank.

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(22, GPIO.OUT)                                # set pin 22 gpio to an output
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)	# Pulldown the input resistor on pin 23
GPIO.output(22, 1)                                      # voltage output voltage for level sensor to 1



while True:
		if GPIO.input(23) == 0:

			print ("The Water Level Is Low")
			time.sleep (2)
		if  GPIO.input(23)== 1:
			print ("Water Level Ok")
			time.sleep (2)



