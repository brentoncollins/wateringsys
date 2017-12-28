#!/usr/bin/python !/

import pyowm
import smtplib
import time
from time import gmtime, strftime
import RPi.GPIO as GPIO 
import plot
from datetime import datetime
import csv
import speedapi


#GPIO Setup
GPIO.setmode(GPIO.BCM)                                                                  # set gpio pinout
GPIO.setwarnings(False)                                                                 # ignore waringing of other files using the gpio
GPIO.setup(22, GPIO.OUT)                                                                # output voltage to level switch
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)                                     # input reading for level switch resistor pulled down.
GPIO.output(22, 1)                                                                      # output voltage to level switch set to set to HIGH.

# Status data
# E-mail settings
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

weather_data = "/home/pi/wateringsys/weather_data.csv"


def csv_writer(time_list=[],temp_list=[],humid_list=[],level_list= []):
	try:			
		with open(weather_data, "w") as output:
			output.truncate()
			writer = csv.writer(output, lineterminator='\n')
			for a,b,c,d in zip(time_list,temp_list,humid_list,level_list):
				writer.writerow([a,b,c,d]) 	
		output.close()
		
	except IOError:
		print('Please open as user that has permission to write to data.csv')
		
def csv_reader_single():
	try:	
		with open(weather_data) as csvfile:
			readCSV = csv.reader(csvfile, delimiter=',')
			time_list=[]
			temp_list=[]
			humid_list=[]
			level_list= []
			try:
				for row in readCSV:
					time_list.append(row[0])
					temp_list.append(row[1])
					humid_list.append(row[2])
					level_list.append(row[3])
			except IndexError:
				print ('Empty List')
				pass
		return time_list,temp_list,humid_list,level_list
		csvfile.close()

	except IOError:
		print('Please open as user that has permission to write to data.csv')

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
		

def weather_observation():
	#try:
		owm = pyowm.OWM('580dcf4a5f151c26f841df7ee95484cd')  # You MUST provide a valid API key
		observation = owm.weather_at_coords(-31.9528, 115.8605)
		w = observation.get_weather()
		humidity = str(w.get_humidity())
		temp = str(w.get_temperature('celsius')['temp'])
		hours12 = time.strftime("%I %p")
		print ("Perth relative humidity is {}".format(humidity))
		print ("Perth temperature is {}".format(temp))
		return hours12,temp,humidity
	#except:
		# I have has this fail to return data once or twice, I dont want it to break the program.
		#pass




def water_level_check():
	global hour_counter
	# Reset the hour counter every 12 hours, I dont wan an email every hour.
	if GPIO.input(23) == 0:   
		if hour_counter == 12:
			hour_counter = 0
		# Only sent the email every 12 hours.
		if hour_counter == 0:
			print ("\nThe Water Level Is Low")
			send_email(g_mail_login, g_mail_password, to_email_1, "Low Water Level","Please fill the water tank")
		# Return the status for the weather data file	
		return "Water level low"
		hour_counter += 1
		
		
	if  GPIO.input(23) == 1:
		hour_counter = 0
		print ("Water Level Ok")
		# Return the status for the weather data file	
		return "Water level OK"
		


if __name__ == "__main__":
	hour_counter = 0
	# Use this counter to only send an email every 12 hours if water level is low
	hours_of_day = [3600,7200,10800,14400,18000,21600,25200,28800,32400,36000,39600,43200,46800,50400,54000,57600,61200,64800,68400,72000,75600,79200,82800,1]
	# Part of the timer, hours in seconds. If the seconds since midnight is exqel to one of these run the main job.
	
	time_list=[]
	temp_list=[]
	humid_list=[]
	water_list = []
	# Empty lists used for the weather data file
	
	def main_job():
		print (time.strftime("%I:%M:%S"))
		print ('\nRunning Moisture, Level, Temp and Plot jobs. The jobs will run on the hour every hour')
		
		# Get the current weather data from the csv file and fill the lists
		time_list,temp_list,humid_list,water_list = csv_reader_single()
		# Get the status of the water level
		water_level = water_level_check()
		# Get the current weather observations
		time_current,temp_current,humid_current = weather_observation()
		
		# Append the valued to the end of each list.
		time_list.append(time_current)
		temp_list.append(temp_current)
		humid_list.append(humid_current)
		water_list.append(water_level)

		# We only want 24 hours fot the plot so if there are 25 in each list delete the first postion in the list which is
		# actually the one from 24 hours ago.
		if len(time_list) >= 25:
			del time_list[0],temp_list[0],humid_list[0],water_list[0]
		# Once the list has been cut down to 24 again including the new data, write to the csv file again
		# ready for reading next time.
		csv_writer(time_list,temp_list,humid_list,water_list)
		# Make the plot images.
		plot.plot_data()
		speedapi.main()
		
		print ("Waiting an hour before testing again.\n")
		
	# Run the mail job first.	
	main_job()
	
	# Start the timer.
	while True:
		time.sleep(1)
		now = datetime.now()
		seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
		# Loop threw the list of hours of the day in seconds, if seconds since midnight is > one of these values but less than 2 seconds
		# after then run the main job.
		for x in hours_of_day:
			if seconds_since_midnight > x and seconds_since_midnight < x + 2:
				print ("Program ran at {} seconds since midnight\n".format(seconds_since_midnight))
				print ("It was set to run at {} seconds since midnight\n".format(x))
				main_job()
				
		

