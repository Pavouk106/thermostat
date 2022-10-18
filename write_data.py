#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time, os.path
from datetime import datetime

debug = False

path_to_files = '/tmp/'

# Print debug function
def debug_print(text):
        if debug:
                print(text)

temp_kids_room = 0
temp_average = 0
hot_water_state = 0
heating_state = 0

# control list:
# 0 - thermostat
# 1 - water valve
control = [0] * 2

while 1:
	# Open dallas temperatures file
	try:
		with open(path_to_files + 'dallas', 'r') as dallas_file:
			dallas_lines = dallas_file.read().splitlines()
			temp_kids_room = dallas_lines[2]
			temp_average = dallas_lines[3]
			dallas_file.close()
			debug_print("DEBUG: Read Dallas ok " + temp_kids_room + " " + temp_average)
	except: # Write -1 (error) if file couldn't be opened
		temp_kids_room = u"---"
		temp_average = u"---"
		debug_print("DEBUG: Read Dallas file failed")
	# If the file was opened and temps were read correctly
	if temp_kids_room != u"---" and temp_average != u"---":
		# If temperature is low in kids room or the average is low AND it'đ daytime, start heating
		if (float(temp_kids_room) < 20.4 or float(temp_average) < 20.4) and (int(datetime.now().hour) < 20 or int(datetime.now().hour) > 8):
			debug_print("STATUS: Temperature low and daytime, heating ON");
			control[0] = 1
		# If both temperatures are good OR it's not daytime, stop heating
		elif (float(temp_kids_room) > 20.6 and float(temp_average) > 20.6) or (int(datetime.now().hour) > 20 or int(datetime.now().hour) < 8):
			debug_print("STATUS: Temperature ok or night, heating OFF")
			control[0] = 0
	else:
		# pricist errory
		debug_print("DEBUG: Dallas read failed, error logged")
		pass

	# Open buttons states file
	try:
		with open(path_to_files + 'states', 'r') as states_file:
			states_lines = states_file.read().splitlines()
			hot_water_state = states_lines[0]
			heating_state = states_lines[1]
			states_file.close()
			debug_print("DEBUG: Read states ok " + hot_water_state + " " + heating_state)
	except: # Write -1 (error) if file couldn't be opened
		hot_water_state = -1
		heating_state = -1
		debug_print("DEBUG: Read states file failed")
	# If the file was opened and states are correct (0 or 1)
	if hot_water_state != -1 and heating_state != -1:
		# podminky na zapnuti vody nebo topeni
		debug_print("STATUS: ")
	else:
		#pricist errory
		debug_print("DEBUG: States read failed, error logged")

	# Podminka zkontroluje, jestli je nekde aktivni změna (zapnuto) a jestli je nekde error (tzn. -1); pri vsech errorech zapise 0 (vsechno vypne), kdyz bude jen nekolik erroru a platny pozadavek, zapise pozadavek
	#if errory a pozadavky
	time.sleep(1)
