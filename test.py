water_level_data = "/home/pi/wateringsys/water_level.txt"

def empty_level_writer(hour):
	try:	
		with open(water_level_data,"w") as f:

				run_status = f.write(hour)
				f.close()
	except IOError:
		print('Please open as user that has permission to write to water_level.txt')

def empty_level_reader():
	try:	
		with open(water_level_data,"r") as f:
			run_status = f.readline()
		
			f.close()
			return run_status
	except IOError:
		print('Please open as user that has permission to write to water_level.txt')
		
		

try:
	hour_counter = int(empty_level_reader())
except ValueError:
	hour_counter = 0
	
print hour_counter
empty_level_writer(str(hour_counter + 1))

try:
	hour_counter = int(empty_level_reader())
except ValueError:
	hour_counter = 0
	
print hour_counter	