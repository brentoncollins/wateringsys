#!/usr/bin/python
#!/

import RPi.GPIO as GPIO
import time
import sys

GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT)
GPIO.setwarnings(False)
GPIO.setup(4, GPIO.OUT)
GPIO.setup(24, GPIO.OUT)                                # set gpio pin 24 to an output as to turn the pump on when needed
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)     # set gpio pin 23 as an inpuut to monitor if the water level is sufficent 
GPIO.output(24, 0)

pumptimer = int(sys.argv[1])

def timer():

	for i in range(1, pumptimer , +1):
		m, s = divmod(i, 60)
		h, m = divmod(m, 60)
		times = "%d Hour %02d Minutes %02d Seconds" % (h, m, s)
		with open("pump.txt", 'w') as f:
				f.close()
		print "Pump Running " + str(i)
		with open("pump.txt", 'a') as x:
				x.write("Pump Running " + str(times))
		time.sleep(1)

def pumprun():
		
	try:	
		if  GPIO.input(23)== 1: 
			GPIO.output (24 ,1)
			GPIO.output (4 ,1)
			print('The pump Will now run for ' + str(pumptimer) + ' seconds\n')
			timer()
			GPIO.output (24 ,0)    # it will now turn the pump off
			GPIO.output (4 ,0)
			now = time.strftime('%A %d at %I %p')

			sql = "SELECT * FROM table_posts"
			number_of_rows = int(cursor.execute(sql))
			rows = number_of_rows + 1

			hours12 = time.strftime("%I %p")
			sql = "insert into table_posts (id,sensor, time, status) VALUES (%d,'Pump Running', '%s' , 'Web Run %d Seconds')" % (rows,now,pumptimer)
			number_of_rows = cursor.execute(sql)
			db.commit()   # you need to call commit() method to save

		else:
			if  GPIO.input(23)== 0:
				print "\nWater level is low, pump will not run\n"

	except Exception as e:
		print(e)
		GPIO.cleanup()                		 # resets all GPIO ports used
		GPIO.output (24 , 0)
		GPIO.output (4 , 0)
			
pumprun()

	





