#!/usr/bin/env python3
import rpi_backlight as bl
import sys

arg = str(sys.argv[1])


if arg == "off":
	#print("\nTurned the back-light off\n")
	bl.set_power(False)
if arg == "on":
	#print("Turned the back-light on")
	bl.set_power(True)

