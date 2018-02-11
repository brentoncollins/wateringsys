#!/usr/bin/env python3
# This script grabs a heap of MYSQL data and plots it with matplotlib, still learing..... please be gentle.....

import sys
from itertools import chain
import matplotlib
matplotlib.use('Agg') ## This helps output the image???
import matplotlib.pyplot as plt
import numpy as np
import math
import csv
import gc
# Data files
weather_data = "/home/pi/wateringsys/weather_data.csv"
plot_image = '/home/pi/wateringsys/temp.png'

def csv_reader_single():
	try:
		#If running only one plot read the csv, create new lists and return them.
		with open(weather_data) as csvfile:
			readCSV = csv.reader(csvfile, delimiter=',')
			time_list=[]
			temp_list=[]
			humid_list=[]

		
			for row in readCSV:

				time_list.append(row[0])
				temp_list.append(float(row[1]))
				humid_list.append(float(row[2]))

		return time_list,temp_list,humid_list


		csvfile.close()	
	except:
		print ("Check if list is empty or youb have file permision.")

def plot_data():
	try:
		hour,pertemp,perthhumid = csv_reader_single()
	
		
		hour.reverse()
		pertemp.reverse()
		perthhumid.reverse()

	
		### STARTING THE PLOT ###
		
		x = np.arange(1,len(hour)+1)	# STEPPED BY 1??? DIRECTING THE AMOUNT OF X AXIS POINTS, +1 WITH THE LENGHT OF THE TIME [LIST] 										

		
		fig, ax1 = plt.subplots()	## set the plot type with the first plot as ax1 figsize=(20, 10)
		plt.grid()							## set the grit behind the plot
		#s1 = np.arange(1,len(time)+1)		## setting the lenght of x and the spacing/occorance but it has already been done..
		ax1.plot(x, pertemp, c='#FF6347', label='Perth Temperature') ##palctemp		## setting the plot line, x for the bottom points, temp to take the y points on the plot, color
		#ax1.set_xlabel('Time of day')		## set the x spine lable
		ax1.set_ylabel('Temperature', color='#FF6347')	# Make the y-axis label, ticks and tick labels match the line color.
		ax1.tick_params('y', colors='#FF6347')	## set the ???? work it out later?
		ax1.set_yticks(np.arange(round(min(pertemp))-2, max(pertemp)+2, 2.0))	## set the arangment of y ticks max and minimum, I have rounded the
														## minumus number in the list of temp due to it being a float and minus 5 for the lower and done the same for the max temp.
		ax1.set_xticklabels( hour, rotation=45 )		## set the x labels on a 45 degree angle
		plt.xticks(x,hour)								## set the x ticks to all the values in time... investigate if nessisary.
		

		ax3 = ax1.twinx()								## ADD another plot
		s3 = np.arange(1,len(hour)+1)
		ax3.plot(x, perthhumid, c = '#006400', label='Relative Humidity') #3 balchumidity
		ax3.set_ylabel('Relative Humidity', color='#006400')
		ax3.tick_params('y', colors='#006400')
		nearesthumidity = int(math.ceil((min(perthhumid) / 10.0))) * 10
		ax3.set_yticks(np.arange(nearesthumidity -5, max(perthhumid)+5, 5))
		ax3.spines['right'].set_position(('axes', 1.07))					## MOVE SPINE TO THE RIGHT A LITTLE FURTHER.
		
		h1, l1 = ax1.get_legend_handles_labels()
		h3, l3 = ax3.get_legend_handles_labels()
		plt.legend(h1+h3, l1+l3, loc=1)
		
		fig.tight_layout()
		fig.set_size_inches(6.4, 3.30)
		plt.gcf().subplots_adjust(bottom=0.22)
		plt.savefig(plot_image, dpi=100)	# save the figure to file
		print ("Weather Plot Complete...")
		gc.collect()
	except TypeError:
		pass
