#!/usr/bin/python
# -*- coding: utf-8 -*-

import serial, time, os.path, urllib, re
#from urllib import urlopen

debug = True

path_to_files = '/tmp/'

serial_port = "/dev/ttyUSB0"
serial_rate = 115200
arduino = serial.Serial(serial_port, serial_rate)
#arduino = serial.Serial(port = None)
#arduino.port = serial_port
#arduino.baudrate = serial_rate
arduino.bytesize = serial.EIGHTBITS
arduino.parity = serial.PARITY_NONE
arduino.stopbits = serial.STOPBITS_ONE
arduino.timeout = 2
arduino.xonxoff = False
arduino.rtscts = False
arduino.dsrdtr = False
arduino.writeTimeout = 0
time.sleep(2.5)
#arduino.open()
arduino.flushInput()
arduino.flushOutput()
arduino.write("t".encode())
#arduino.close()
time.sleep(2.5)

main_temp_values = [None] * 2
humidity_values = [None] * 2
voltage_values = [None] * 2

temps_values = [None] * 3
dallas_address = [
"28-0416b35d80ff", # PC stul
"28-0516c110d6ff", # Skrinka
"28-0316b5e979ff", # Detsky pokoj
]

# Print debug function
def debug_print(text):
	if debug:
		print(text)

while 1:
	debug_print("DEBUG: Reading data")

	if arduino.isOpen():
		debug_print("DEBUG: Arduino connected")
		arduino.flushInput()
		arduino.flushOutput()
		arduino.write("t".encode())
		for x in range(0, 1): # Can be deleted after transitioning to BME (or other external temp)
			output = arduino.readline().rstrip("\r\n".encode())
			debug_print("DEBUG: Arduino temperature " + str(x) + ": " + output.decode())
			if float(output) <= 70 and float(output) >= -50:
				main_temp_values[x] = round(float(output), 1)
			else:
				main_temp_values[x] = u"---"
			local_temps_file = open(path_to_files + 'local_temps', 'w')
			local_temps_file.write("%s\n" % main_temp_values[x])
			local_temps_file.close()
			arduino.readline()
		arduino.write("h".encode())
		for x in range(0, 1): # Can be deleted after transitioning to BME (or other external humidity)
			output = arduino.readline().rstrip("\r\n".encode())
			debug_print("DEBUG: Arduino humidity " + str(x) + ": " + output.decode())
			if float(output) <= 100 and float(output) >= 0:
				humidity_values[x] = round(float(output), 1)
			else:
				humidity_values[x] = u"---"
			humidity_file = open(path_to_files + 'local_humidity', 'w')
			humidity_file.write("%s\n" % humidity_values[x])
			humidity_file.close()
			arduino.readline()

		# Teploty z kotelny
		temps_file = open(path_to_files + 'temps', 'w')
		try:
			data = urllib.urlopen("http://control.pavoukovo.cz/temps").read().decode() # Otevrit soubor
			if data.find("html") == -1:
				temps_file.write(data)
				debug_print("DEBUG: HTTP temps read ok")
			else:
				for i in range(0, 8):
					temps_file.write("%s\n" % u"---") # Kdyz se nepodari otevrit soubor, zapsat ---
				debug_print("DEBUG: " + time.strftime("%H:%M:%S") + " HTTP temps read failed, remote file not found")
		except:
			for i in range(0, 8):
				temps_file.write("%s\n" % u"---") # Kdyz se nepodari otevrit soubor, zapsat ---
			debug_print("DEBUG: " + time.strftime("%H:%M:%S") + " HTTP temps read failed")
		temps_file.close()

		# Udaje z bazenu/meteobudky
		meteo_file = open(path_to_files + 'meteo', 'w')
		try:
			data = urllib.urlopen("http://meteo.pavoukovo.cz/meteo").read().decode() # Otevrit soubor
			if data.find("html") == -1:
				meteo_file.write(data)
				debug_print("DEBUG: HTTP meteo read ok")
			else:
				for i in range(0, 7):
	                                meteo_file.write("%s\n" % u"---") # Kdyz se nepodari otevrit soubor, zapsat ---
	                        debug_print("DEBUG: " + time.strftime("%H:%M:%S") + " HTTP meteo read failed, remote file not found")
		except:
			for i in range(0, 7):
				meteo_file.write("%s\n" % u"---") # Kdyz se nepodari otevrit soubor, zapsat ---
			debug_print("DEBUG: " + time.strftime("%H:%M:%S") + " HTTP meteo read failed")
		meteo_file.close()

		# Rychlost vetru
		wind_file = open(path_to_files + 'wind', 'w')
		try:
			debug_print("Wind start")
			data = urllib.urlopen("http://wind.pavoukovo.cz/wind").read().decode() # Otevrit soubor
			debug_print("Wind opened")
			if data.find("html") == -1:
				debug_print("Wind HTML found")
				wind_file.write(data)
				debug_print("DEBUG: HTTP wind read ok")
			else:
				debug_print("Wind bad reply")
				for i in range(0, 5):
					wind_file.write("%s\n" % u"---") # Kdyz se nepodari otevrit soubor, zapsat ---
				debug_print("DEBUG: " + time.strftime("%H:%M:%S") + " HTTP wind read failed, remote file not found")
		except:
			debug_print("Wind open failed")
			for i in range(0, 5):
				wind_file.write("%s\n" % u"---") # Kdyz se nepodari otevrit soubor, zapsat ---
			debug_print("DEBUG: " + time.strftime("%H:%M:%S") + " HTTP wind read failed")
		wind_file.close()

		# Dallas teplotni cidla
		for i in range(0, len(dallas_address)): # Smycka pro cteni podle zadanych adres
			try:
				temp_file = open('/sys/bus/w1/devices/' + dallas_address[i] + '/w1_slave', 'r') # Otevrit soubor s daty
				file_lines = temp_file.read().splitlines()
				crc = re.compile('crc=.. (.*)')
				crc_value = crc.search(file_lines[0])
				debug_print(crc_value.group(1))
				if crc_value.group(1) == "YES": # Overit kontrolni soucet
					temp = re.compile('t=(.*)')
					temp_value = temp.search(file_lines[1])
					debug_print(temp_value.group(1))
					if temp_value.group(1) != "85000": # Pokud neukazuje 85 stupnu, coz je chybovy stav
						temps_values[i] = float(temp_value.group(1)) / 1000 # Ulozit teplotu
					else:
						temps_values[i] = u"---" # Kdyby ukazoval 85, tak ulozit ---
				else:
					temps_values[i] = u"---" # Kdyz neni kontrolni souce v poradku, zapsat ---
			except:
				temps_values[i] = u"---" # Kdyz se nepovede otevrit soubor s daty, zapsat ---
				debug_print("DEBUG: " + "/sys/bus/w1/devices/" + dallas_address[i] + "/w1_slave" + " Temp read failed")
		dallas_file = open(path_to_files + 'dallas', 'w') # Otevrit soubor pro zapsani teplot
		for i in range(0, len(temps_values) + 1):
			if i < len(temps_values) and temps_values[i] == u"---": # Kdyz je misto teploty ulozeno ---, nejde zaokrouhlit (aby nespadl program)
				dallas_file.write("%s\n" % temps_values[i]) # Ulozit rovnou ---
			elif i < len(temps_values):
				dallas_file.write("%s\n" % round(temps_values[i], 1)) # Ulozit zaokrouhlenou teplotu
			elif main_temp_values[0] == u"---" or (u"---" in temps_values and i == len(temps_values)): # Vyjimka,  pokud je nekde ulozeno ---, nepocitat prumer (aby nespadl program)
				dallas_file.write("%s\n" % u"---")
			elif i == len(temps_values): # DO posledniho radku ulozit prumer teplot
				dallas_file.write("%s\n" % round((temps_values[0] + temps_values[1] + main_temp_values[0]) / 3, 1)) # Prumer se pocita jen z teplot v obyvaku a "hlavni teploty" (na vypinaci v kuchyni)
		dallas_file.close()
	time.sleep(5)
