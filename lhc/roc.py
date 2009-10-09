#!/usr/bin/python 

import numpy

try:
	import psyco
	psyco.full()
except ImportError:
	sys.stderr.write('Unable to import psyco')

X = 0 # True positives
Y = 1 # False positives
A = 2 # Area under curve
T = 3 # Threshold

def roc(points, pve):
	"""
	points: sorted list of points in the form [[value, class]]
	pve: the symbol for the class with low values.
	"""
	global X, Y, A, T
	
	length = len(points) + 1
	data = numpy.empty( (4, length) , dtype=numpy.float32)
	data[X, 0] = 0; data[Y, 0] = 0; data[A, 0] = 0
	data[T, 0] = points[0][0]
	
	for i in xrange(length-1):
		if points[i][1] == pve:
			data[X, i+1] = data[X, i]
			data[Y, i+1] = data[Y, i] + 1
			data[A, i+1] = data[A, i]
		else:
			data[X, i+1] = data[X, i] + 1
			data[Y, i+1] = data[Y, i]
			data[A, i+1] = data[A, i] + data[Y, i+1]
	
		data[T, i+1] = points[i][0]
	#data[A,:] = data[A,:] / data[A:-1]
	return data

def getRates(roc):
	res = numpy.empty((4, len(roc)), dtype=numpy.float32)

def parseLine(line):
	parts = line.split()
	parts[0] = float(parts[0])
	return parts

def main(argv = None):
	global X, Y, A, T
	
	if len(argv) != 3:
		print 'Usage ./roc.py <infile> <class>'
		sys.exit(1)
	
	infile = file(argv[1])
	infile.readline()
	points = [parseLine(line) for line in infile]
	points.sort()
	infile.close()
	
	data = roc(points, argv[2])
	nCol, nRow = data.shape
	
	outfile = file(argv[1][:-3] + 'roc', 'w')
	outfile.write('x\ty\ta\tt\n')
	i = 0
	while i < nRow:
		outfile.write(str(data[X, i]) + '\t' + str(data[Y, i]) + '\t' + str(data[A, i]) + '\t' + str(data[T, i]) + '\n')
		i += 1
	outfile.close()

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))