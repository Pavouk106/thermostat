#!/usr/bin/python
# -*- coding: utf-8 -*-

import pygame, sys, datetime, time, serial, os.path, codecs, math
from pygame.locals import *
from time import strftime

wind_angle = 15 # Angle of rotation of wind display

debug = 0
path_to_files = '/tmp/'

window_width = 480
window_height = 320

pygame.init()
clock = pygame.time.Clock()
display = pygame.display.set_mode((0, 0), pygame.FULLSCREEN|pygame.HWSURFACE|pygame.DOUBLEBUF)

# Colors
black = (0, 0, 0)
white = (255, 255, 255)
red = (255, 0, 0)
red_dark = (63, 0, 0)
green = (0, 255, 0)
green_dark = (0, 63, 0)
grey_dark = (63, 63, 63)

border = 20
main_temp_vertical_divider = 300
divider_border = border / 2
degrees_text_offset = 40
main_temp_text_offset = 150


# Text sizes
size_text_header = 18
size_text_main_temp = 100
size_text_degrees = 30
size_text_humidity = 20
size_text_clock = 32
size_text_status = 14
size_text_default = 14
size_text_button = 18
size_space_small = 8
size_space_large = 10

# Text fonts
text_header = pygame.font.Font('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size_text_header)
text_main_temp = pygame.font.Font('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size_text_main_temp)
text_degrees = pygame.font.Font('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size_text_degrees)
text_humidity = pygame.font.Font('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size_text_humidity)
text_clock = pygame.font.Font('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size_text_clock)
text_status = pygame.font.Font('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size_text_status)
text_default = pygame.font.Font('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size_text_default)
text_button = pygame.font.Font('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', size_text_button)

# State of buttons
buttons_pressed = [0, 0, 0, 0]

main_temp_names = [u"Uvnitř", u"Venku"] 
temp_names = [None] * 8 # Will get filled from reading a file

# Values arrays/lists
main_temp_values = [None] * 2
humidity_values = [None] * 2
temp_values = [None] * 8
wind_values = [None] * 5
pool_temp_values = [None] * 2

heating_time = 1800 # How long to run heating, in seconds
heating_time_end = heating_time # When the heating should end
heating_time_show = 0 # What to show on button

# Where we are (navigation); 0 = "screensaver", 1 = Showing temps + time + buttons
window_type = 1

draw_static_gui = 1 # Very probably is not used
pygame.mouse.set_pos(0, 0) # Resets the mouse when starting the GUI
x, y = (0, 0)

# Whole section may not be needed
previous_time = 0
previous_date = 0
previous_redraw_time = 0

# Print debug
def debug_print(text):
        if debug:
                print(text)

# Function to use various text
def text_objects(text, font, color): # (what to show, what font to use, what color should it be) - selects from presets
	textSurface = font.render(text, True, color)
	return textSurface, textSurface.get_rect()

# Draws buttons + sets their states
def button_on_off(index, text_line1, text_line2, color_text, position_x, position_y, width, height, color_off, color_off_border, color_on, color_on_border):
	global x, y
	button = pygame.Rect(position_x, position_y, width, height)
	#x, y = event.pos
	if button.collidepoint(x, y):
		if buttons_pressed[index] == 0:
			buttons_pressed[index] = 1
		else:
			buttons_pressed[index] = 0
		x, y = (0, 0)
	if buttons_pressed[index] == 1:
		button_background_rect = pygame.draw.rect(display, color_on_border, (position_x, position_y, width, height));
		pygame.draw.rect(display, color_on, (position_x + 2, position_y + 2, width - 4, height - 4));
	else:
		button_background_rect = pygame.draw.rect(display, color_off_border, (position_x, position_y, width, height));
		pygame.draw.rect(display, color_off, (position_x + 2, position_y + 2, width - 4, height - 4));
	TextSurf, TextRect = text_objects(text_line1, text_button, color_text)
	TextRect.center = (position_x + width / 2, position_y + height / 2 - size_text_button / 2)
	display.blit(TextSurf, TextRect)
	TextSurf, TextRect = text_objects(text_line2, text_default, color_text)
	TextRect.center = (position_x + width / 2, position_y + height / 2 + size_text_button / 2)
	display.blit(TextSurf, TextRect)
	#pygame.display.update(button_background_rect)
	#pygame.display.update(TextRect)

# Should be able to use button_on_off instead
def button_default(index, text, color_text, position_x, position_y, width, height, color, color_border):
	global window_type
	button = pygame.Rect(position_x, position_y, width, height)
	x, y = event.pos
	if button.collidepoint(x, y):
		# předělat na window_type / přepínání­ oken
		if buttons_pressed[index] == 0:
			buttons_pressed[index] = 1
		else:
			buttons_pressed[index] = 0
	button_background_rect = pygame.draw.rect(display, color_border, (position_x, position_y, width, height));
	pygame.draw.rect(display, color, (position_x + 2, position_y + 2, width - 4, height - 4));
	TextSurf, TextRect = text_objects(text + u" (" + str(buttons_pressed[index]) + u")", text_button, color_text)
	TextRect.center = (position_x + width / 2, position_y + height / 2)
	display.blit(TextSurf, TextRect)
	pygame.display.update(button_background_rect)
	pygame.display.update(TextRect)

def compass_line(color, angle, length, width):
	if length == "long":
		pygame.draw.line(display, color, (main_temp_vertical_divider + border + 65 + round(45 * math.sin(math.radians(angle + wind_angle))), 0 + border + 70 + border + 70 + border + 45 - round(45 * math.cos(math.radians(angle + wind_angle)))), (main_temp_vertical_divider + border + 65 + round(30 * math.sin(math.radians(angle + wind_angle))), 0 + border + 70 + border + 70 + border + 45 - round(30 * math.cos(math.radians(angle + wind_angle)))), width)
	elif length == "short":
		pygame.draw.line(display, color, (main_temp_vertical_divider + border + 65 + round(45 * math.sin(math.radians(angle + wind_angle))), 0 + border + 70 + border + 70 + border + 45 - round(45 * math.cos(math.radians(angle + wind_angle)))), (main_temp_vertical_divider + border + 65 + round(35 * math.sin(math.radians(angle + wind_angle))), 0 + border + 70 + border + 70 + border + 45 - round(35 * math.cos(math.radians(angle + wind_angle)))), width)

# Rework needed - add repeated reads if one fails; rework may not be needed if FPS is 5
# 2022 - rework probably not needed, backend reworked instead
def read_data():
	global main_temp_values, humidity_values, temp_values, temp_names, wind_values

	try:
		with open(path_to_files + 'main_temps', 'r') as main_temp_file:
			main_temp_lines = main_temp_file.read().splitlines()
			main_temp_values[0] = main_temp_lines[0]
			main_temp_values[1] = main_temp_lines[1]
			main_temp_file.close()
			#if (len(main_temp_values) == 0):
			#	main_temp_values[0] = u"---"
	except:
		main_temp_values[0] = u"---"
		debug_print("DEBUG: " + strftime("%H:%M:%S") + " " + path_to_files + "dallas read failed or reading sensors failed")
		pass

	try:
		with open(path_to_files + 'meteo', 'r') as meteo_file:
			meteo_lines = meteo_file.read().splitlines()
			meteo_file.close()
			# Tenhle radek netreba
			# main_temp_values[1] = str(round(float(meteo_lines[2]), 1))
			pool_temp_values[0] = str(round(float(meteo_lines[0]), 1))
			pool_temp_values[1] = str(round(float(meteo_lines[1]), 1))
	except:
		main_temp_values[1] = u"---"
		pool_temp_values[0] = u"---"
		pool_temp_values[1] = u"---"
		debug_print("DEBUG: " + strftime("%H:%M:%S") + " " + path_to_files + "meteo temp read failed")
		pass

	try:
		with open(path_to_files + 'local_humidity', 'r') as humidity_file:
			humidity_lines = humidity_file.read().splitlines()
			humidity_values[0] = humidity_lines[0]
			humidity_file.close()
			#if (len(humidity_values) == 0):
			#	humidity_values[0] = [u"---"];
	except:
		humidity_values[0] = u"---"
		debug_print("DEBUG: " + strftime("%H:%M:%S") + " " + path_to_files + "local_humidity read failed")
		pass
	try:
		with open(path_to_files + 'meteo', 'r') as meteo_file:
			meteo_lines = meteo_file.read().splitlines()
			meteo_file.close()
			humidity_values[1] = str(round(float(meteo_lines[5]), 1))
	except:
		humidity_values[1] = u"---"
		debug_print("DEBUG: " + strftime("%H:%M:%S") + " " + path_to_files + "meteo humidity read failed")
		pass

	try:
		with open(path_to_files + 'wind', 'r') as wind_file:
			wind_values = wind_file.read().splitlines()
			wind_file.close()
			if (len(wind_values) == 0):
				wind_values = [u"---"] * 5;
	except:
		wind_values = [u"---"] * 5;
		debug_print("DEBUG: " + strftime("%H:%M:%S") + " " + path_to_files + "wind read failed")
		pass

	temp_names_file = codecs.open('/home/pi/software/thermostat/temp_names', 'r', 'utf-8')
	temp_names = temp_names_file.read().splitlines()
	temp_names_file.close()

	try:
		with open(path_to_files + 'temps', 'r') as temp_values_file:
			temp_values = temp_values_file.read().splitlines()
			temp_values_file.close()
			if (len(temp_values) == 0):
				temp_values = [u"---"] * 8;
	except:
		temp_values = [u"---"] * 8;
		debug_print("DEBUG: " + strftime("%H:%M:%S") + " " + path_to_files + "temps read failed")
		pass

def write_data():
	global buttons_pressed
	buttons_file = open(path_to_files + 'states', 'w')
	for i in range(0, len(buttons_pressed)):
		buttons_file.write("%s\n" % buttons_pressed[i])
	buttons_file.close()

def window_main(window_type, mouse_click):
	global heating_time_end
	read_data()
	if window_type == 1:
		pygame.draw.rect(display, black, (0, 0, 480, 320))
		# Draw time
		# clock_rect = pygame.draw.rect(display, black, (divider_top + border, border + size_text_default, window_width - 2 * border - divider_top, size_text_main_temp))
		#TextSurf, TextRect = text_objects(strftime("%H:%M"), text_default, white)
		#TextRect.bottomright = (window_width - border - 100, window_height - border)
		#display.blit(TextSurf, TextRect)
		#pygame.display.update(clock_rect)

		# Draw date
		#date_rect = pygame.draw.rect(display, black, (divider_top + border, border + size_text_default + size_text_clock + size_space_small, window_width - 2 * border - divider_top, size_text_default))
		#TextSurf, TextRect = text_objects(strftime("%d. %m. %Y"), text_default, white)
		#TextRect.bottomright = (window_width - border, window_height - border)
		#display.blit(TextSurf, TextRect)
		#pygame.display.update(date_rect)

		# Out temp + humidity
		TextSurf, TextRect = text_objects(main_temp_values[0], text_main_temp, white)
		TextRect.topright = (main_temp_vertical_divider - divider_border - degrees_text_offset, 0 + border)
		display.blit(TextSurf, TextRect)
		TextSurf, TextRect = text_objects(u"\u00b0" + "C", text_degrees, white)
		TextRect.bottomright = (main_temp_vertical_divider - divider_border, 0 + border + size_text_main_temp)
		display.blit(TextSurf, TextRect)
		TextSurf, TextRect = text_objects(main_temp_names[0], text_humidity, white)
		TextRect.topleft = (main_temp_vertical_divider - divider_border - main_temp_text_offset, 0 + border + size_text_main_temp)
		display.blit(TextSurf, TextRect)
		TextSurf, TextRect = text_objects(str(humidity_values[0]) + " %", text_humidity, white)
		TextRect.topright = (main_temp_vertical_divider - divider_border, 0 + border + size_text_main_temp)
		display.blit(TextSurf, TextRect)

		# In temp + humidity
		TextSurf, TextRect = text_objects(main_temp_values[1], text_main_temp, white)
		TextRect.topright = (main_temp_vertical_divider - divider_border - degrees_text_offset, 0 + border + size_text_main_temp + size_text_humidity + border + border / 2)
		display.blit(TextSurf, TextRect)
		TextSurf, TextRect = text_objects(u"\u00b0" + "C", text_degrees, white)
		TextRect.bottomright = (main_temp_vertical_divider - divider_border, 0 + border + + size_text_main_temp + size_text_main_temp + size_text_humidity + border + border / 2)
		display.blit(TextSurf, TextRect)
		TextSurf, TextRect = text_objects(main_temp_names[1], text_humidity, white)
		TextRect.topleft = (main_temp_vertical_divider - divider_border - main_temp_text_offset, 0 + border + size_text_main_temp + size_text_main_temp + size_text_humidity + border + border / 2)
		display.blit(TextSurf, TextRect)
		TextSurf, TextRect = text_objects(str(humidity_values[1]) + " %", text_humidity, white)
		TextRect.topright = (main_temp_vertical_divider - divider_border, 0 + border + size_text_main_temp + size_text_main_temp + size_text_humidity + border + border / 2)
		display.blit(TextSurf, TextRect)

		# Button for water heating + text on it
		button_on_off(0, u"Ohřev vody", str(temp_values[4]) + "/" + str(temp_values[5]) + " " + u"\u00b0" + "C", white, main_temp_vertical_divider + border, 0 + border, 130, 45, red_dark, red, green_dark, green)

		# Button for heating
		if heating_time_end != heating_time:
			minutes = str(int((heating_time_end - int(time.time())) / 60))
			seconds = (heating_time_end - int(time.time())) % 60
			if seconds < 10:
				seconds = "0" + str(seconds)
			else:
				seconds = str(seconds)
			heating_time_show = minutes + ":" + seconds
		else:
			minutes = str(int(heating_time / 60))
			seconds = heating_time % 60
			if seconds < 10:
				seconds = "0" + str(seconds)
			else:
				seconds = str(seconds)
			heating_time_show = minutes + ":" + seconds
		button_on_off(1, u"Ruční topení", heating_time_show, white, main_temp_vertical_divider + border, 0 + border + 35 + border, 130, 45, red_dark, red, green_dark, green)

		# Button for pool
		if pool_temp_values[0] == u"---" and pool_temp_values[1] == u"---":
			temp_string = "---"
		else:
			if float(pool_temp_values[1]) - float(pool_temp_values[0]) >= 0:
				temp_string = str(pool_temp_values[0]) + u"\u00b0" + "C (+" + str(float(pool_temp_values[1]) - float( pool_temp_values[0])) + ")"
			else:
				temp_string = str(pool_temp_values[0]) + u"\u00b0" + "C (-" + str(abs(float(pool_temp_values[1]) - float( pool_temp_values[0]))) + ")"
#				temp_string = str(pool_temp_values[0]) + u"(" + "-" + str(abs(float(pool_temp_values[1]) - float( pool_temp_values[0]))) + " " + u"\u00b0" + "C)"
		button_on_off(2, u"Bazén", temp_string, white, main_temp_vertical_divider + border, 0 + border + 35 + border + 35 + border, 130, 45, red_dark, red, green_dark, green)

		# Compass for wind direction and speed
		pygame.draw.circle(display, white, (main_temp_vertical_divider + border + 65, 0 + border + 70 + border + 70 + border + 45), 45 , 2)
		compass_line(white, 0, "long", 3)
		compass_line(white, 45, "short", 1)
		TextSurf, TextRect = text_objects("S", text_default, white)
		TextRect.center = (main_temp_vertical_divider + border + 65 + round((45 + 10) * math.sin(math.radians(wind_angle))), 0 + border + 70 + border + 70 + border + 45 - round((45 + 10) * math.cos(math.radians(wind_angle))))
		display.blit(TextSurf, TextRect)
		compass_line(white, 90, "long", 3)
		compass_line(white, 135, "short", 1)
		TextSurf, TextRect = text_objects("V", text_default, white)
		TextRect.center = (main_temp_vertical_divider + border + 65 + round((45 + 10) * math.sin(math.radians(90 + wind_angle))), 0 + border + 70 + border + 70 + border + 45 - round((45 + 10) * math.cos(math.radians(90 + wind_angle))))
		display.blit(TextSurf, TextRect)
		compass_line(white, 180, "long", 3)
		compass_line(white, 225, "short", 1)
		TextSurf, TextRect = text_objects("J", text_default, white)
		TextRect.center = (main_temp_vertical_divider + border + 65 + round((45 + 10) * math.sin(math.radians(180 + wind_angle))), 0 + border + 70 + border + 70 + border + 45 - round((45 + 10) * math.cos(math.radians(180 + wind_angle))))
		display.blit(TextSurf, TextRect)
		compass_line(white, 270, "long", 3)
		compass_line(white, 315, "short", 1)
		TextSurf, TextRect = text_objects("Z", text_default, white)
		TextRect.center = (main_temp_vertical_divider + border + 65 + round((45 + 10) * math.sin(math.radians(270 + wind_angle))), 0 + border + 70 + border + 70 + border + 45 - round((45 + 10) * math.cos(math.radians(270 + wind_angle))))
		display.blit(TextSurf, TextRect)
		TextSurf, TextRect = text_objects(str(wind_values[0]), text_button, white)
		TextRect.midbottom = (main_temp_vertical_divider + border + 65, 0 + border + 70 + border + 70 + border + 45)
		display.blit(TextSurf, TextRect)
		TextSurf, TextRect = text_objects("(" + str(wind_values[1]) + ")", text_default, white)
		TextRect.midtop = (main_temp_vertical_divider + border + 65, 0 + border + 70 + border + 70 + border + 45)
		display.blit(TextSurf, TextRect)

		if wind_values[1] != "0.0" and wind_values[0] != u"---":
			if int(wind_values[4]) % 90:
				compass_line(red, int(wind_values[4]), "long", 5)
			else:
				compass_line(red, int(wind_values[4]), "long", 5)

		pygame.display.update();

while True:
#	global x, y, heating_time, heating_time_end
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
			x, y = event.pos
			pygame.mouse.set_pos(0, 0)
			#window_main(window_type, 1)

	window_main(window_type, 0)

	# Continue running heating time even if in another menu
	if buttons_pressed[1] == 0:
		heating_time_end = heating_time
	elif buttons_pressed[1] == 1 and heating_time_end == heating_time:
		heating_time_end = int(time.time()) + heating_time
	elif buttons_pressed[1] == 1 and heating_time_end < int(time.time()):
		heating_time_end = heating_time
		buttons_pressed[1] = 0
	# Write state data in the file
	write_data()

	# Ověření překreslování­ (výpis timestamp)
#	current_redraw_time = int(time.time())
#	if previous_redraw_time + 5 <= current_redraw_time:
#		previous_redraw_time = current_redraw_time
#		redraw_rect = pygame.draw.rect(display, black, (0, window_height - size_text_default, 150, size_text_default))
#		TextSurf, TextRect = text_objects(str(current_redraw_time), text_default, white)
#		TextRect.topleft = (0, window_height - size_text_default)
#		display.blit(TextSurf, TextRect)
#		pygame.display.update(redraw_rect)

#	pygame.draw.line(display, white, (divider_top / 2, border), (divider_top / 2, divider_horizontal))
#	pygame.display.update()

	# Show framerate
#	TextSurf, TextRect = text_objects(str(clock.get_fps()), text_default, white)
#	TextRect.bottomright = (window_width, window_height)
#	display.blit(TextSurf, TextRect)
#	pygame.display.update()

	clock.tick(10)
