import serial
import sane
import time
import os
import numpy

# Yar 'MERCA
mm_per_in = 25.40005


print sane.init()

scanner = sane.open([id for (id, maker, model, desc) in sane.get_devices() if model == "LiDE 110"][0])

print "Acquired Scanner", scanner.get_options()
scanner.resolution = 300 # 300dpi

# US standard letter
scanner.br_x = mm_per_in * 8.5
scanner.br_y = mm_per_in * 11

# print scanner.opt.keys()

print scanner['resolution']
print scanner['tl_x'] # zero
print scanner['tl_y'] # zero
print scanner['br_x'] # nonzero
print scanner['br_y'] # nonzero

ser = serial.Serial('/dev/ttyACM0', 9600)
while True:
	print "Waiting for lid close event"
	line = ser.readline()
	print "Got line", line
	if line.strip() != "Lid closed":
		continue	
	print "Acquired Scanner", scanner
	im = scanner.scan()
	print "Acquired Output", im
	year = time.strftime("%Y")
	date = time.strftime("%d %b")
	if not os.path.exists(year):
		os.makedirs(year)
	narwhal = numpy.array(im.histogram())
	mean_color = numpy.average(range(0, 256), weights = narwhal)
	# find da stdev
	
	im.save(year + "/" + date, "JPEG")