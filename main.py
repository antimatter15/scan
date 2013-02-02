import serial
import sane
import time
import os
import numpy
from PIL import Image, ImageFilter

# Yar 'MERCA
mm_per_in = 25.40005
blank = Image.open("blank.jpg")
blank.filter(ImageFilter.BLUR)

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
	im.filter(ImageFilter.BLUR)

	print "Acquired Output", im
	year = time.strftime("%Y")
	date = time.strftime("%d %b")
	if not os.path.exists(year):
		os.makedirs(year)
	
	# narwhal = numpy.array(im.histogram())
	# mean = numpy.sum(numpy.dot(range(0, 256), narwhal)) / numpy.sum(narwhal)
	# mean_square = numpy.sum(numpy.dot(numpy.square(range(0, 256)), narwhal)) / numpy.sum(narwhal)
	# variance = mean_square - numpy.square(mean)
	# print mean, mean_square, variance, numpy.sqrt(variance)
	
	# normal_hist = [numpy.exp(-numpy.square(x - mean)/(2 * variance)) / numpy.sqrt(2 * numpy.pi * variance) for x in range(0, 256)]

	# normal_hist = numpy.array(blank.histogram())

	# diff = narwhal - normal_hist
	# print numpy.std(diff), numpy.mean(diff), numpy.sum(numpy.square(diff))
	# print diff, narwhal, normal_hist

	# find da stdev

	diff = im - blank

	im.save(year + "/" + date, "JPEG")
	diff.save(year + "/" + date + "-diff", "JPEG")