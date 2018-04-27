#!/usr/bin/env python3

import csv
import sys
from crontab import CronTab

timer_data = '/home/pi/wateringsys/timer_data.csv'
run_time = int(sys.argv[1])
repeat = int(sys.argv[2])
run_length = int(sys.argv[3])

try:
	cron = CronTab(user=True)
	cron.remove_all(comment='water_timer')
	cron.write()

	# Insert new cron job timer.
	cron = CronTab(user=True)
	job = cron.new(
		command='sudo python3 /home/pi/wateringsys/crontimer.py {}'.format(run_length),
		comment='water_timer')
	if repeat == 1:
		job.hour.on(run_time)
		job.minute.on(0)
	if repeat >= 2:
		job.setall(0, run_time, '*/{}'.format(repeat), None, None)
	cron.write()

	with open(timer_data, "w") as output:
		output.truncate()
		writer = csv.writer(output, lineterminator='\n')
		writer.writerow([run_time, repeat, run_length])
		output.close()
	
	
	
	print ('The timer has been set')
except:
	print ('Setting the timer failed')