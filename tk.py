#!/usr/bin/env python3
import time
from tkinter import *
from PIL import ImageTk, Image
import random
import csv
# import spur
import os
import sys
from subprocess import Popen
import RPi.GPIO as GPIO
from subprocess import call
import rpi_backlight as bl
from datetime import datetime

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(22, GPIO.OUT, initial= 1)                # Set pin 22 gpio to an output
GPIO.setup(23, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)	# Pulldown the input resistor on pin 23
GPIO.setup(24, GPIO.OUT, initial= 0)                # Set gpio pin 24 to an output as to turn the pump on when needed

#Main window
root= Tk()

root_status_string = StringVar()	# Live timer countdown
timer_input_value = IntVar()		# Keypad textbox value 1
daily_timer_input_value = IntVar()	# Keypad textbox value 2
timer_set_run_text = StringVar()	# Text string showing output of timer.
timer_recurrence_string = 0			# How often the pump will run
timer_time_string = ""				# What time the pump will run
timer_status = StringVar()			# Timer info on set text
water_level = StringVar()			# Current water level string
timer_error_string = StringVar()	# Timer set error string
timer_status_1 = StringVar()		# Timer data info on set text

# Convert data from input value to mins/seconds
min, sec = divmod(int(daily_timer_input_value.get()), 60)		
hour, min = divmod(min, 60)

# Image/CSV data
keyboard_image = "keypad.jpg"
timer_data = 'timer_data.csv'
plot_img = "temp.png"
screen_off = "perl /home/pi/wateringsys/screen-off.pl"
speed_image = "speed.png"

class numpad():

	def __init__(self):

		# Setup number pad screen
		self.number_pad = Toplevel(root)
		self.keypad_entery = Entry(self.number_pad,width=5,font=("Helvetica", 55))
		self.keypad_entery.grid(row=0, column=0, columnspan=3, ipady=5)
		self.number_pad.attributes('-fullscreen',True)

		# Variables of keeys to loop though
		self.keys = [
		['1', '2', '3'],    
		['4', '5', '6'],    
		['7', '8', '9'],    
		['Clear', '0', 'Exit'], ]
		
		# Loop threw the keys and create the button with lambda command
		for self.y, self.row in enumerate(self.keys, 1):
			for self.x, self.key in enumerate(self.row):
				self.b = Button(self.number_pad, text=self.key, command=lambda val=self.key:__numb_enter(val))
				self.b.grid(row=self.y, column=self.x, ipadx=108, ipady=30)
		self.exit = Button(self.number_pad, text = "Exit", command = self.number_pad.destroy).grid(row=self.y, column=self.x, ipadx=100, ipady=30)
		# Set the exit button at the end of the loop
		
		def __numb_enter(arg):
			# All globals required for updating the timer daily_timer_input_value
			global timer_set_run_text
			global timer_recurrence_string
			global timer_time_string
			global min
			global sec
			global timer_error_string
			self.pin = '' 
			# Set the pin var to empty
			if arg == 'Clear':
				# remove last number from `pin`
				self.pin = self.pin[:-1]
				self.keypad_entery.delete('0', 'end')
				self.keypad_entery.insert('end', self.pin)

			elif arg == 'Exit':
				self.number_pad.destroy
				# Exit the keypad window
			else:
				# add number to pin
				self.pin += arg
				# add number to `entry`
				self.keypad_entery.insert('end', arg)
				self.pad_val = self.keypad_entery.get()
				daily_timer_input_value.set(self.pad_val)
				timer_input_value.set(self.pad_val)
				# Set calculate the minuts and seconds for the label
				min, sec = divmod(int(self.pad_val), 60)
				hour, min = divmod(min, 60)
				# Set the label to update the current seconds/minutes
				timer_set_run_text.set("The timer will run at {} every {} day(s) for {} Minutes {} Seconds".format(timer_time_string,timer_recurrence_string,min,sec))
				
class timers(object):

	def __init__(self):
		
		global timer_set_run_text
		global daily_timer_input_value
		global timer_status
		global timer_error_string
		global keyboard_img
		self.timer_set_page = Toplevel(root)
		# Setup the window for the timer selections
		# Strings for all of the buttons
		
		self.timer_run_text = Label(self.timer_set_page,text="Please choose a time of day to run the pump.",font = ('Helvetica',20)).grid(row = 1,columnspan=8)
		self.hours_in_day = [["1AM","2AM","3AM","4AM","5AM","6AM","7AM","8AM"\
		],["9AM","10AM","11AM","12PM","1PM","2PM","3PM","4PM"],[\
		"5PM","6PM","7PM","8PM","9PM","10PM","11PM","12AM"]]
		
		self.timer_entery = Entry(self.timer_set_page, textvariable=daily_timer_input_value, width= 23).grid(row = 9,columnspan=3,column=0)		
		# Entery box for run time
		daily_timer_input_value.set("")													# Set the entery to blank
		self.keyboard_button = Button(self.timer_set_page,command=numpad)				# Button Image to open number pad
		self.keyboard_img = ImageTk.PhotoImage(Image.open(keyboard_image))				#
		self.keyboard_button.config(image=self.keyboard_img)							#
		self.keyboard_button.image = self.keyboard_img									# Keep an instance of the image so
		self.keyboard_button.grid(row = 9,sticky=E,columnspan=2,column=1)				# that it doesnt get garbage collected
		self.exit = Button (self.timer_set_page, text = "Exit", command = self.timer_set_page.destroy).grid(row=9, columnspan=4,column=6, ipadx=50, ipady=15)
																						# Exit button back to main screen
		self.set_timer = Button (self.timer_set_page, text = "Set Timer", command = self.__set_timer_csv,bg="green").grid(row=9, columnspan=4,column=3, ipadx=50, ipady=15)
																						# Set the timer outputs the data to CVS
		self.timer_run_text = Label(self.timer_set_page,textvariable=timer_set_run_text,font = ('Helvetica',14)).grid(row = 10,columnspan=8)
																						# Set the text variable for timer run label
		
		timers.timer_run_failed = Label(self.timer_set_page,textvariable=timer_status,font = ('Helvetica',14),foreground='red')
		timers.timer_run_failed.grid(row = 11,columnspan=8)			# Set the text variable for a failed CSV
		timer_status.set("")
		
		timers.err_label = Label(self.timer_set_page,textvariable=timer_error_string,font = ('Helvetica',14),foreground='red')
		timers.err_label.grid(row = 12,columnspan=8)				# Set the text variable for a failed CSV
		timer_error_string.set("")
		
		self.timer_length_text = Label(self.timer_set_page,text="Please choose how long to run the timer for in seconds.",font = ('Helvetica',20)).grid(row = 7,columnspan=8)
		
		self.z = 0
	
		# Loop threw the hours in the day z will provide the hour of the day to return in lambda to timer_return function
		# which manipulates the string and outputs to the label
		for self.y, self.row in enumerate(self.hours_in_day, 1):
			for self.x, self.key in enumerate(self.row):
				self.z += 1
				if self.z == 24:
					self.z = 0
				self.b = Button(self.timer_set_page, text=self.key, command=lambda val=self.z:self.__timer_return(val))
				self.b.grid(row=self.y + 1, column=self.x, ipadx=20, ipady=10)
		
		self.timer_set_page.attributes('-fullscreen',True)

		# Strings for all recurrence rate
		self.recurrence = ["1 Day","2 Day","3 Day","4 Day","5 Day","6 Day","7 Day"]
		self.timer_reoc_text = Label(self.timer_set_page,text="Please choose how often you would like to run the timer.",font = ('Helvetica',20)).grid(row = 5,columnspan=8)
		
		self.r = 0
		self.col = 0
		# Loop threw the reoccurance options r will provide the amount of days between running and return in lambda to recurrence_return function
		# which manipulates the string and outputs to the label
		for self.d in self.recurrence:
			self.r += 1

			self.c = Button(self.timer_set_page, text=self.d, command=lambda val=self.r:self.__recurrence_return(val))
			self.c.grid(row=6, column=self.col, ipadx=12, ipady=12)
			self.col += 1
		
	def __clear_entery(self):
			daily_timer_input_value.set("")
			timer_input_value.set("")
			
			
	def __recurrence_return(self,arg):
		global timer_set_run_text
		global timer_recurrence_string
		global timer_time_string
		global min
		global sec
		
		# retrieve the reoccorance rate, and set the new label string
		timer_recurrence_string = str(arg)
		timer_set_run_text.set("The timer will run at {} every {} day(s) for {} Minutes {} Seconds".format(timer_time_string,timer_recurrence_string,min,sec))

		
	def __timer_return(self,arg):
		global timer_set_run_text
		global timer_recurrence_string
		global timer_time_string
		global min
		global sec
		
		# retrieve the time of day, and set the new label string
		self.pump_run_time = str(arg)
		timer_time_string = str(str(arg) +":00")
		if len(timer_time_string) <= 4:
			timer_time_string = "0" + timer_time_string
		timer_set_run_text.set("The timer will run at {} every {} day(s) for {} Minutes {} Seconds".format(timer_time_string,timer_recurrence_string,min,sec))

	
	def __set_timer_csv(self):
		global timer_status
		global timer_status_1
		
		# Write all of the variables to CSV file.
		try:
			run_time = self.pump_run_time
			repeat = str(timer_recurrence_string)
			run_length = str(daily_timer_input_value.get())
			with open(timer_data, "w") as self.output:
				self.output.truncate()
				self.writer = csv.writer(self.output, lineterminator='\n')
				self.writer.writerow([run_time,repeat,run_length]) 					
				self.output.close()
			# Set both enterys back to empty
			daily_timer_input_value.set("")
			timer_input_value.set("")
			
			call(["sudo", "systemctl", "restart" ,"pumptimer.service"])	
			timers.timer_run_failed.config(fg="Green")
			timer_status.set("The timer has been set.")
			timer_status_1.set(str(timer_time_string))
		except:
			timers.timer_run_failed.config(fg="Red")
			timers.err_label.config(fg="Red")
			timer_status_1.set(str(timer_time_string))
			timer_status.set("Please enter a time, recurrence rate and timer length")
		

def timer(): # Simple timer class, 
	try: # If any errors usually due to no input pass
	
		run_time = timer_input_value.get()
		root_status_string.set(str("Pump Running"))
		timer_input_value.set("")

		if  GPIO.input(23)== 1: 
			GPIO.output (24 ,1)
			for i in range(1, run_time + 1 , +1):
				m, s = divmod(i, 60)
				h, m = divmod(m, 60)
				root_status_string.set(str("{} Minutes {} Seconds".format(m, s)))
				root.update()
				time.sleep(1)
			GPIO.output (24 ,0)
		
		root_status_string.set(str("The pump run has finished"))
	except:
		GPIO.output (24 ,0)			# Turn the pump off.
		print ("failed")
		pass



manual_timer = 0

def man_start(force=True):
	global running
	global manual_timer
	try:

		if force:
			running = True
		if running:
			if  GPIO.input(23)== 1: 
				root_status_string.set(str("Pump Running"))
				GPIO.output (24 ,1)
				manual_timer += 1
				m, s = divmod(manual_timer, 60)
				h, m = divmod(m, 60)
				root_status_string.set(str("{} Minutes {} Seconds".format(m, s)))
				root.update()
				root.after(1000, man_start, False)
			if  GPIO.input(23)== 0:
				root_status_string.set(str("The pump will not run when the water level is low."))
	except:
		GPIO.output (24 ,0)		# Stop the pump.
def man_stop():
	global running
	global manual_timer	
	GPIO.output (24 ,0)

	running = False
	manual_timer = 0
	root_status_string.set(str("The Pump has been manually stopped."))
	
def img_updater(): # Auto image updater for home screen.
	# Open image
		try:
			global counter

			

			
			
			timer_set_time,time_until_run = csv_read()

			if GPIO.input(23) == 0:
				water_level_label.config(fg="Red")
				water_level.set(str("The water level is LOW."))
			if  GPIO.input(23)== 1:
				water_level_label.config(fg="Green")
				water_level.set(str("The water level is OK."))
			
			# Every 10 seconds change the timer_status_1 string which is the label on the front page.
			counter += 1
			if counter >= 1:
				timer_status_1.set(str(timer_set_time))
				
				plant_stat_img = ImageTk.PhotoImage(Image.open(plot_img))
				plant_stat_panel.config(image = plant_stat_img)
				plant_stat_panel.image = plant_stat_img
			
				
			if counter >= 11:
				timer_status_1.set(str(time_until_run))
				
				speed_img = ImageTk.PhotoImage(Image.open(speed_image))#/home/pi/html/
				plant_stat_panel.config(image = speed_img)
				plant_stat_panel.image = speed_img
				

			if counter >= 21:
				counter = 0
			
			# Reload page every 10 seconds
			root.after(1000, img_updater)
		
		except:
			timer_status_1.set(str('Please enter a timer, there is currently no timer set.'))
			root.after(1000, img_updater)
			pass
		
def back_light():
	#Start the perl script which turns off the screen backlight when the screensaver is active.
	#The perl script calls backlight.py which turns the backlight on and off.
	proc = Popen([screen_off], shell=True,
             stdin=None, stdout=None, stderr=None, close_fds=True)

def csv_read():
	# Consider changing the times of day to a dict to use AM PM times inline with the loop.
	try:	
		with open(timer_data) as csvfile:
			readCSV = csv.reader(csvfile, delimiter=',')
			for row in readCSV:
				days = int(row[1])
				runtime = int(row[2])
				time_of_day = int(row[0])
			csvfile.close()
			#Due to using plain numbers in the number pad loop must convert it to something people can read.
			# Following is to read the set timer and make a label out of it.
			
			if int(int(row[0])) <= 9:
				run_hour = "0{}:00".format(str(int(row[0])))
			if int(int(row[0])) >= 10:
				run_hour = "{}:00".format(str(int(row[0])))
				
			days = int(row[1])
			m, s = divmod(int(row[2]), 60)
			h, m = divmod(m, 60)
			run_time = (str("{} Minutes and {} Seconds".format(m, s)))
			
			current_runtime = "The timer is set to run for {} every {} day(s) at {}".format(run_time,days,run_hour)
			
			# the following is to read the set timer and print out how much time is left on the timer.
			
			now = datetime.now()
			seconds_since_last_run = (now - now.replace(hour=time_of_day, minute=0, second=0, microsecond=0)).total_seconds()  
			if days == 1:
				total_seconds = (days - 1) * 86400
				countdown = total_seconds - int(round(seconds_since_last_run))
				if countdown <=1:
					total_seconds = days * 86400
					countdown = total_seconds - int(round(seconds_since_last_run))
			if days > 1:
				total_seconds = (days - 1) * 86400
				countdown = total_seconds - int(round(seconds_since_last_run))
				
			m, s = divmod(countdown, 60)
			h, m = divmod(m, 60)
			d, h = divmod(h, 24)
				
			times = ("There is {} day(s) {} hour(s) {} minute(s) and {} seconds remaining on the timer.".format(d,h,m,s))
			
			# Return the strings.
			return current_runtime, times
	except IndexError:
		timer_status_1.set(str("Please set a pump timer."))
		

## Buttons

pump_manual_start_button = Button(root,text="Start Pump Manual",command=man_start, height = 3, width = 15,bg="green").grid(row = 0, sticky=E,column =1,rowspan =2)
pump_manual_stop_button = Button(root,text="Stop Pump Manual",command=man_stop, height = 3, width = 15,bg="red").grid(row = 0, sticky=E,column =2,rowspan =2)
keyboard_button = Button(root,command=numpad)
keyboard_img = ImageTk.PhotoImage(Image.open(keyboard_image))
keyboard_button.config(image=keyboard_img)
keyboard_button.image = keyboard_img
keyboard_button.grid(row = 2,sticky=E)

timer_button = Button(root,text= "Set Timer", command = timers, height = 3, width = 15).grid(row = 5,column =2)
pump_timer_start_button=Button(root,text="Start Pump Timer",command = timer).grid(row = 2, sticky=W)


## Labels
hedding_label=Label(root,text="Newcastle Pad Watering System",font=("Helvetica", 16)).grid(row = 0)
timer_entery_text = Label(root,text="Please enter how many seconds you wish to run the pump for.").grid(row = 1)
timer_string_label=Label(root,textvariable=root_status_string).grid(row = 3,sticky=N)
plant_stat_panel = Label(root)
plant_stat_panel.grid(row = 5,column = 0, columnspan=2, sticky = W )
current_timer_label=Label(root,textvariable=timer_status_1).grid(row = 4,columnspan =2,sticky=S)

# If you want to dynamicaly alter the state of the lable later on you need to asign the grid seperatly 
# otherwise it just returns a None type when trying to change it.

water_level_label=Label(root,textvariable=water_level,font=("Times New Roman", 16))
water_level_label.grid(row = 2,column =1,columnspan =2,sticky=E)

## Enterys

timer_entery = Entry(root, textvariable=timer_input_value, width = 15).grid(row = 2)
timer_input_value.set("")

counter = 0
## Main Loop

root.attributes('-fullscreen',True)		# Run Fullscreen.
root.after(0,img_updater)				# Run "img_updater" function on startup.
root.after(0, back_light)
root.mainloop()							# Run the main page.
