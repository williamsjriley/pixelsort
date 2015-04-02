from PIL import Image, ImageFilter
import random
import string
import sys
import math
import argparse

p = argparse.ArgumentParser(description="pixel mangle an image")
p.add_argument("image", help="input image file")
p.add_argument("-o", "--output", help="output image file, defaults to %input%-sorted.png")
p.add_argument("-i", "--int_function", help="random, edges, waves, file, none",default="random")
p.add_argument("-f", "--int_file", help="image for intervals",default="in.png")
p.add_argument("-t", "--threshold", help="between 0 and 255*3",default=100)
p.add_argument("-c", "--clength", help="characteristic length",default=50)
p.add_argument("-r", "--randomness", help="what % of intervals are NOT sorted",default=0)
p.add_argument("-m", "--multichannel", help="'y' enables multichannel mode",default='n')
args = p.parse_args()

randomness = int(args.randomness)
threshold = int(args.threshold)
clength = int(args.clength)

print "Randomness =", randomness, "%"
print "Threshold =", threshold
print "Characteristic length = ", clength

black_pixel = (0, 0, 0, 255)
white_pixel = (255, 255, 255, 255)

# Generates names for output files
def id_generator(size=5, chars=string.ascii_lowercase + string.ascii_uppercase + string.digits):
	return ''.join(random.choice(chars) for _ in range(size))

if args.output:
	outputImage = args.output
else:
	outputImage = id_generator()+".png"

# Sorts a given row of pixels, can handle individual channels as well
def sort_interval(interval):
	if interval == []:
		return []
	elif isinstance(interval[0], tuple):
		return(sorted(interval, key = lambda x: x[0] + x[1] + x[2]))
	else:
		return(sorted(interval, key = lambda x: x))

# Generates random widths for intervals. Used by int_random()
def random_width():
	x = random.random()
	# width = int(200*(1-(1-(x-1)**2)**0.5))
	width = int(clength*(1-x))
	# width = int(50/(x+0.1))
	return(width)

# Functions starting with int return intervals according to which to sort
def int_edges(pixels):
	img = Image.open(args.image)
	edges = img.filter(ImageFilter.FIND_EDGES)
	edges = edges.convert('RGBA')
	edge_data = edges.load()

	filter_pixels = []
	edge_pixels = []
	intervals = []

	print("Defining edges...")
	for y in range(img.size[1]):
		filter_pixels.append([])
		for x in range(img.size[0]):
			filter_pixels[y].append(edge_data[x, y])

	print("Thresholding...")
	for y in range(len(pixels)):
		edge_pixels.append([])
		for x in range(len(pixels[0])):
			if filter_pixels[y][x][0] + filter_pixels[y][x][1] + filter_pixels[y][x][2] < threshold:
				edge_pixels[y].append(white_pixel)
			else:
				edge_pixels[y].append(black_pixel)

	print("Cleaning up edges...")
	for y in range(len(pixels)-1,1,-1):
		for x in range(len(pixels[0])-1,1,-1):
			if edge_pixels[y][x] == black_pixel and edge_pixels[y][x-1] == black_pixel:
				edge_pixels[y][x] = white_pixel

	print("Defining intervals...")
	for y in range(len(pixels)):
		intervals.append([])
		for x in range(len(pixels[0])):
			if edge_pixels[y][x] == black_pixel:
				intervals[y].append(x)
		intervals[y].append(len(pixels[0]))
	return(intervals)

def int_random(pixels):
	intervals = []

	print("Defining intervals...")
	for y in range(len(pixels)):
		intervals.append([])
		x = 0
		while True:
			width = random_width()
			x += width
			if x > len(pixels[0]):
				intervals[y].append(len(pixels[0]))
				break
			else:
				intervals[y].append(x)
	return(intervals)

def int_waves(pixels):
	intervals = []

	print("Defining intervals...")
	for y in range(len(pixels)):
		intervals.append([])
		x = 0
		while True:
			width = clength + random.randint(0,10)
			x += width
			if x > len(pixels[0]):
				intervals[y].append(len(pixels[0]))
				break
			else:
				intervals[y].append(x)
	return(intervals)

def int_file(pixels):
	intervals = []
	file_pixels = []

	img = Image.open(args.int_file)
	img = img.convert('RGBA')
	data = img.load()
	for y in range(img.size[1]):
		file_pixels.append([])
		for x in range(img.size[0]):
			file_pixels[y].append(data[x, y])

	print("Cleaning up edges...")
	for y in range(len(pixels)-1,1,-1):
		for x in range(len(pixels[0])-1,1,-1):
			if file_pixels[y][x] == black_pixel and file_pixels[y][x-1] == black_pixel:
				file_pixels[y][x] = white_pixel

	print("Defining intervals...")
	for y in range(len(pixels)):
		intervals.append([])
		for x in range(len(pixels[0])):
			if file_pixels[y][x] == black_pixel:
				intervals[y].append(x)
		intervals[y].append(len(pixels[0]))

	return intervals

def int_file_edges(pixels):
	img = Image.open(args.int_file)
	edges = img.filter(ImageFilter.FIND_EDGES)
	edges = edges.convert('RGBA')
	edge_data = edges.load()

	filter_pixels = []
	edge_pixels = []
	intervals = []

	print("Defining edges...")
	for y in range(img.size[1]):
		filter_pixels.append([])
		for x in range(img.size[0]):
			filter_pixels[y].append(edge_data[x, y])

	print("Thresholding...")
	for y in range(len(pixels)):
		edge_pixels.append([])
		for x in range(len(pixels[0])):
			if filter_pixels[y][x][0] + filter_pixels[y][x][1] + filter_pixels[y][x][2] < threshold:
				edge_pixels[y].append(white_pixel)
			else:
				edge_pixels[y].append(black_pixel)

	print("Cleaning up edges...")
	for y in range(len(pixels)-1,1,-1):
		for x in range(len(pixels[0])-1,1,-1):
			if edge_pixels[y][x] == black_pixel and edge_pixels[y][x-1] == black_pixel:
				edge_pixels[y][x] = white_pixel

	print("Defining intervals...")
	for y in range(len(pixels)):
		intervals.append([])
		for x in range(len(pixels[0])):
			if edge_pixels[y][x] == black_pixel:
				intervals[y].append(x)
		intervals[y].append(len(pixels[0]))
	return(intervals)

def int_none(pixels):
	intervals = []
	for y in range(len(pixels)):
		intervals.append([len(pixels[0])])
	return(intervals)

# Get function to define intervals from command line arguments
if args.int_function == "random":
	int_function = int_random
elif args.int_function == "edges":
	int_function = int_edges
elif args.int_function == "waves":
	int_function = int_waves
elif args.int_function == "file":
	int_function = int_file
elif args.int_function == "file-edges":
	int_function = int_file_edges
elif args.int_function == "none":
	int_function = int_none
else:
	print "Error! Invalid interval function."

# Sorts each channel separately
def sort_image_multichannel(pixels, intervalses):
	sorted_pixels = []
	# Separate pixels into channels
	channels = []
	for channel in [0, 1, 2]:
		channels.append([])
		for y in range(len(pixels)):
			channels[channel].append([])
			for x in range(len(pixels[0])):
				channels[channel][y].append(pixels[y][x][channel])

	# sort the channels separately
	for channel in [0, 1, 2]:
		channels[channel] = sort_image(channels[channel],intervalses[channel])
	for y in range(len(pixels)):
		sorted_pixels.append([])
		for x in range(len(pixels[0])):
			sorted_pixels[y].append((channels[0][y][x], channels[1][y][x], channels[2][y][x], 255))
	return(sorted_pixels)

# Sorts the image
def sort_image(pixels, intervals):
	print("Sorting intervals...")
	# Hold sorted pixels
	sorted_pixels=[]
	for y in range(len(pixels)):
		row=[]
		xMin = 0
		for xMax in intervals[y]:
			interval = []
			for x in range(xMin, xMax):
				interval.append(pixels[y][x])
			if random.randint(0,100)>=randomness:
				row = row + sort_interval(interval)
			else:
				row = row + interval
			xMin = xMax
		row.append(pixels[y][0]) # wat
		sorted_pixels.append(row)
	return(sorted_pixels)

def pixel_sort():
	print("Opening image...")
	img = Image.open(args.image)
	img = img.convert('RGBA')

	print("Getting data...")
	data = img.load()
	new = Image.new('RGBA', img.size)

	pixels = []

	print("Getting pixels...")
	for y in range(img.size[1]):
		pixels.append([])
		for x in range(img.size[0]):
			pixels[y].append(data[x, y])

	if args.multichannel == 'y': # If multichannel mode is enabled
		intervalses = []		 # intervalses: List of intervals
		for channel in [0, 1, 2]:
			intervalses.append(int_random(pixels))
		sorted_pixels = sort_image_multichannel(pixels, intervalses)
	else:
		intervals = int_function(pixels)
		sorted_pixels = sort_image(pixels, intervals)

	print("Placing pixels...")
	for y in range(img.size[1]):
		for x in range(img.size[0]):
			new.putpixel((x, y), sorted_pixels[y][x])

	print("Saving image...")
	new.save(outputImage)
	print "Done!", outputImage

pixel_sort()
