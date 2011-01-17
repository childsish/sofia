#!/usr/bin/python 

import numpy

X = 0 # True positives
Y = 1 # False positives
A = 2 # Area under curve
T = 3 # Threshold

def roc(clss, vals):
	""" clss: boolean. True if positive case, False if the negative case
	vals: list of real numbers.
	"""
	global X, Y, A, T
	
	clss = clss[numpy.argsort(vals)]
	vals = numpy.sort(vals)
	
	length = len(clss) + 1
	data = numpy.empty( (4, length) , dtype=numpy.float32)
	data[X, 0] = 0; data[Y, 0] = 0; data[A, 0] = 0
	data[T, 0] = clss[0]
	
	for i in xrange(length-1):
		if clss[i]:
			data[X, i+1] = data[X, i]
			data[Y, i+1] = data[Y, i] + 1
			data[A, i+1] = data[A, i]
		else:
			data[X, i+1] = data[X, i] + 1
			data[Y, i+1] = data[Y, i]
			data[A, i+1] = data[A, i] + data[Y, i+1]
	
		data[T, i+1] = vals[i]
	return data

def getRates(roc):
	res = numpy.empty((4, len(roc)), dtype=numpy.float32)

def parseLine(line):
	parts = line.split()
	parts[0] = float(parts[0])
	return parts

def main(argv = None):
	global X, Y, A, T
	
	infile = file(argv[1])
	infile.readline()
	points = numpy.array([map(float, line.split()) for line in infile])
	infile.close()
	
	data = roc(points[:,0], points[:,1])
	nCol, nRow = data.shape
	
	sys.stdout.write('x\ty\ta\tt\n')
	for i in xrange(1, nRow):
		sys.stdout.write('%.0f\t%.0f\t%.0f\t%.3f\n'%\
		 (data[X,i], data[Y,i], data[A,i], data[T,i]))

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
