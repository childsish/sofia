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
	
	order = numpy.argsort(vals)
	clss = numpy.array(clss)[order]
	vals = numpy.array(vals)[order]
	
	length = len(clss) + 1
	data = numpy.empty( (length, 4) , dtype=numpy.float32)
	data[0, X] = 0; data[0, Y] = 0; data[0, A] = 0
	data[0, T] = clss[0]
	
	for i in xrange(length-1):
		if clss[i]:
			data[i+1, X] = data[i, X]
			data[i+1, Y] = data[i, Y] + 1
			data[i+1, A] = data[i, A]
		else:
			data[i+1, X] = data[i, X] + 1
			data[i+1, Y] = data[i, Y]
			data[i+1, A] = data[i, A] + data[i+1, Y]
	
		data[i+1, T] = vals[i]
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
