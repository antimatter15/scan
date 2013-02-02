# Here be the configs!

dimensions = (8.5, 11) # standard letter size paper
resolution = 300 # 300dpi is good
margins = 0.5 # half an inch, for placement errors, etc

import serial
import sane
import time
import os
import numpy
from PIL import Image, ImageFilter, ImageChops

blank = Image.open("blank.jpg")
blank.filter(ImageFilter.BLUR)

# Yar 'MERCA
mm_per_in = 25.4000

print "Initializing SANE"

print sane.init()

scanner = sane.open([id for (id, maker, model, desc) in sane.get_devices() if model == "LiDE 110"][0])

print "Acquired Scanner", scanner

scanner.resolution = resolution
scanner.br_x = mm_per_in * dimensions[0]
scanner.br_y = mm_per_in * dimensions[1]

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
	blurred = im.filter(ImageFilter.BLUR)

	print "Acquired Output", im

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
	(width, height) = blurred.size
	n = int(margins * resolution) # half inch margins
	diff = ImageChops.difference(blurred, blank).crop((n, n, width - n, height - n))
	minimized = diff.filter(ImageFilter.MinFilter(3))
	change = numpy.sum(minimized.histogram()[10:]) / float(width * height)

	# this metric seems to have a pretty good differentiation boundary
	# a mostly white sheet of paper with a few sketches scores 1e-2
	# and blank scores between 1e-7 to 1e-6

	if change < 0.001:
		print "This appears to be a blank image", change
		continue

	year = time.strftime("%Y")
	month = time.strftime("%b %Y")
	date = time.strftime("%d %b")
	
	if not os.path.exists(year):
		os.makedirs(year)
	
	if not os.path.exists(year + "/" + month):
		os.makedirs(year + "/" + month)

	def fn(num):
		return '%s/%s/%s %03d.jpg' % (year, month, date, num)

	imax = 1
	# exponential backoff style
	while os.path.exists(fn(imax)):
		imax *= 2

	if imax > 2:
		# binary search type thing
		imin = imax / 2
		while imin < imax:
			midpoint = imin / 2 + imax / 2
			if os.path.exists(fn(midpoint)):
				imin = midpoint + 1
			else:
				imax = midpoint
		imax = imin
		# off by one errors suck
		# while os.path.exists(fn(imax)):
		# 	imax += 1

	im.save(fn(imax), "JPEG")