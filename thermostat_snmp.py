#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, os.path

path_to_files = '/tmp/'

def read_data(file_name):
	global local_temps_values, humidity_values, voltage_values, temps_values, dallas_values
	opened_file = open(path_to_files + file_name, 'r')
	if file_name == 'local_temps':
		local_temps_values = opened_file.read().splitlines()
		while not len(local_temps_values):
			time.sleep(0.05)
			opened_file.seek(0)
			local_temps_values = opened_file.read().splitlines()
	elif file_name == 'local_humidity':
		humidity_values = opened_file.read().splitlines()
		while not len(humidity_values):
			time.sleep(0.05)
			opened_file.seek(0)
			humidity_values = opened_file.read().splitlines()
#	elif file_name == 'sensor_voltage':
#		voltage_values = opened_file.read().splitlines()
#		while not len(voltage_values):
#			time.sleep(0.05)
#			opened_file.seek(0)
#			voltage_values = opened_file.read().splitlines()
	elif file_name == 'temps':
		temps_values = opened_file.read().splitlines()
		while not len(temps_values):
			time.sleep(0.05)
			opened_file.seek(0)
			temps_values = opened_file.read().splitlines()
	elif file_name == 'dallas':
		dallas_values = opened_file.read().splitlines()
		while not len(temps_values):
			time.sleep(0.05)
			opened_file.seek(0)
			dallas_values = opened_file.read().splitlines()
	opened_file.close()

def output_data(output_type):
	global local_temps_values, humidity_values, voltage_values, temps_values
	if output_type == 'local_temps':
		for i in xrange(0, 2):
#			if local_temps_values[i] != '---' and float(local_temps_values[i]) <= 70 and float(local_temps_values[i]) >= -50:
#				print local_temps_values[i]
#			else:
			print local_temps_values[i]
	elif output_type == 'local_humidity':
		for i in xrange(0, 2):
#			if humidity_values[i] != '---' and float(humidity_values[i]) <= 100 and float(humidity_values[i]) >= 0:
#				print humidity_values[i]
#			else:
			print humidity_values[i]
#	elif output_type == 'sensor_voltage':
#		for i in xrange(0, 2):
#			if voltage_values[i] != '---':
#				print voltage_values[i]
#			else:
#			print voltage_values[i]
	elif output_type == 'temps':
		for i in xrange(0, 8):
			print temps_values[i]
	elif output_type == 'dallas':
		for i in xrange(0, 4):
			print dallas_values[i]

# No longer used?
while os.path.isfile(path_to_files + 'thermostat.lock'):
	time.sleep(0.1);

#if not os.path.isfile(path_to_files + 'thermostat.lock'):
#	lock_file = open(path_to_files + 'thermostat.lock', 'w')
read_data('local_temps')
read_data('local_humidity')
#read_data('sensor_voltage')
read_data('temps')
read_data('dallas')
	#temp_file = open(path_to_files + 'local_temps', 'r')
	#humidity_file = open(path_to_files + 'local_humidity', 'r')
	#voltage_file = open(path_to_files + 'sensor_voltage', 'r')
	#temp_values = temp_file.read().splitlines()
	#humidity_values = humidity_file.read().splitlines()
	#voltage_values = voltage_file.read().splitlines()
	#temp_file.close()
	#humidity_file.close()
	#voltage_file.close()
#	lock_file.close()
#	os.remove(path_to_files + 'thermostat.lock')
output_data('local_temps')
output_data('local_humidity')
#output_data('sensor_voltage')
output_data('temps')
output_data('dallas')
#else:
#	print '0\n0\n0\n0\n0\n0'
