#!/usr/bin/env python3
import RPi.GPIO as GPIO
import time
import smtplib
import sys

# Setup the GPIO pins.
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(24, GPIO.OUT, initial=0)                                # output voltage level switch
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)     # input for level switch

# Location of the data.

email_data = "/home/pi/wateringsys/email_data.txt"
arg = int(sys.argv[1])


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


def send_email(user, pwd, recipient, subject, body):	# this is the email module.
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
		server.login(user, pwd)
		server.sendmail(FROM, TO, message)
		server.close()
		print('successfully sent the mail')
	except:
		print("failed to send mail")


if GPIO.input(23) == 0:		
	# If GPIO 23 has no input voltage the water level is low.
		print ("The the water level is low the pump will not turn on.")
		send_email(g_mail_login, g_mail_password, to_email_1, "Failed Pump Run",
													"The pump tried to run, it failed to run due to the "
													"water level being low")


if GPIO.input(23) == 1:

	# If GPIO input 23 has a    high input the water level is ok and the pump will run.
	execute_time = time.strftime('%c')
	GPIO.output(24, 1)
	# Set GPIO output 24 output to high to turn the solid state relay on. 
	print("The pump will run for {} seconds".format(arg))
	for x in range(1, arg):
		time.sleep(1)
		if GPIO.input(23) == 0:
			send_email(g_mail_login, g_mail_password, to_email_1, "Failed Pump Run",
														"The pump tried to run, it failed to "
														"run due to the water level being low")
			GPIO.output(24, 0)
			
	# Sleep while the pump runs
	# Set GPIO 24 output to low to turn the solid state relay off.
	GPIO.output(24, 0)
	# Send the email that the pump has run.
	send_email(g_mail_login, g_mail_password, to_email_1,"PUMP TIMER RUN"
															,"The pump timer has run @ {}"
															"".format(execute_time))

	print("\nTimelog Entered\n\nPump timer running for {} seconds".format(str(arg)))



