#!/usr/bin/python
#!/
import RPi.GPIO as GPIO
import time
from datetime import datetime
import smtplib
import csv
import sys

# Setup the GPIO pins.
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(24, GPIO.OUT, initial= 0)                                # output voltage level switch
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)     # input for level switch

# Location of the data.

email_data = "/home/pi/wateringsys/email_data.txt"

def get_data():
	fp = open(email_data)
	login = ""
	passwd = ""
	to_email = ""
	for i, line in enumerate(fp):
		if i == 1:
			login = line
		elif i == 3:
			passwd = line
		elif i == 5:
			to_email = line
	fp.close()
	return login,passwd,to_email
g_mail_login, g_mail_password,to_email_1 = get_data()	

timer_data = "/home/pi/wateringsys/timer_data.csv"




	
def send_email(user, pwd, recipient, subject, body):							# this is the email module.
    gmail_user = user
    gmail_pwd = pwd
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        print ('successfully sent the mail')
    except:
        print ("failed to send mail")



def on_fail():
	# On exception turn off all inputs.
	GPIO.output (24 , 0)

	print ("All outputs turned off")


def csv_reader():
	try:	
		#Read the timer data csv and get the current timer setting to return to the timer.
		with open(timer_data) as csvfile:
			readCSV = csv.reader(csvfile, delimiter=',')
			for row in readCSV:
				time_of_day = int(row[0])
				days = int(row[1])
				runtime = int(row[2])
			return days,runtime,time_of_day
			csvfile.close()
	except UnboundLocalError:
		print ("Timer data file probaby empty exiting")
		sys.exit()
			
def set_timer(days,time_of_day):
	
	now = datetime.now()
	seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
	# Get the seconds since midnight
	
	current_day = now.strftime("%j")
	# Get the current day of the year
	
	# Depending on if the timer is set before or after the time of day that the timer is set
	# It will take a day off
	if seconds_since_midnight < (int(time_of_day) *3600):
		new_day = int(current_day) + (days - 2)
	else:
		new_day = int(current_day) + (days - 1)
		
	# The hour in which the timer should run.
	new_hour = int(time_of_day) *3600
	# The length of time to run the pump.
	new_run_time = (new_day * 86400) + new_hour


	return new_run_time
			
			


while True:
	try:
		try:
			days,runtime,time_of_day = csv_reader()
			# Read the CSV and return the current settings.
		except:
			print('Pump data CSV probably empty or incorrect')
			sys.exit()
		stop_time = set_timer(days,time_of_day)
		# THe stop time is today in seconds plus the total amount of seconds until the next pump run.
		
		while True:
			now = datetime.now()
			seconds_since_newyear = (now - now.replace(month = 1,day=1 ,hour=0, minute=0, second=0, microsecond=0)).total_seconds()
			
			seconds_until_run = stop_time - int(seconds_since_newyear)
			

			m, s = divmod(seconds_until_run, 60)
			h, m = divmod(m, 60)
			d, h = divmod(h, 24)

			time_remaining = ("There is {} day(s) {} hour(s) {} minute(s) and {} seconds remaining on the timer.".format(d,h,m,s))
			print (time_remaining)
			
			time.sleep(1)
			# set_timer returns the total amount of senconds since the newyear that the timer should be set, not sure if
			# this will beak on new years eve
			if seconds_since_newyear > stop_time:

				if GPIO.input(23) == 0:		
					while True:
						if GPIO.input(23) == 0:		
						# If GPIO 23 has no input voltage the water level is low.
							print ("The the water level is low the pump will not turn on.")
							send_email(g_mail_login, g_mail_password, to_email_1,"Failed Pump Run",\
							"The pump tried to run, it failed to run due to the water level being low")
							print ("Sleeping for 6 hours.")
							time.sleep(60)
							
						else:
							# When breaking out of the loop stop_time will set the new stop_time in seconds since newyear.
							break
					
				if  GPIO.input(23)== 1:

				# If GPIO input 23 has a high input the water level is ok and the pump will run.
					execute_time = time.strftime('%c')
					GPIO.output (24 , 1)
					# Set GPIO output 24 output to high to turn the solid state relay on. 
					print ("The pump will run for {} seconds".format(runtime))	
					time.sleep (runtime)		
					# Sleep while the pump runs
					# Set GPIO 24 output to low to turn the solid state relay off.
					GPIO.output (24 , 0)
					# Send the email that the pump has run.
					send_email(g_mail_login, g_mail_password, to_email_1,"PUMPTIMER RUN",\
					"The pumptimer has run @ {}".format(execute_time))

					print("\nTimelog Entered\n\nPump timer running for {} seconds".format(str(runtime)))
					# When breaking out of the loop stop_time will set the new stop_time in seconds since newyear.
					break


		
	except Exception as e:
		#Turn off the pump output.
		on_fail()
		output = str(e)
		print (output)
		send_email(g_mail_login, g_mail_password, to_email_1,"PUMPTIMER FAILED",\
		"The pumptimer has failed @ {}\n The error was - \n {}".format((str(time.strftime)),output))
		time.sleep(60)

