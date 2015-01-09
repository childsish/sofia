#!/usr/bin/python

import numpy

def bonferroni(data):
	return data * len(data)

def benjaminiHochberg(data):
	""" Dirk's version. """
	n = len(data)
	res = numpy.empty(data.shape, dtype=data.dtype)
	
	order = numpy.argsort(data, 0)[::-1]
	
	res[order[0]] = data[order[0]]
	for i in xrange(1, len(order)):
		r = float(n - i) # Rank
		if data[order[i]] * n / r > res[order[i-1]]:
			res[order[i]] = res[order[i-1]]
		else:
			res[order[i]] = data[order[i]] * n / r
	
	return res

def main():
	import random
	data = range(20)
	#random.shuffle(data)
	data = numpy.array(data, dtype=numpy.float32) / 80.
	
	
	print data
	print bonferroni(data)
	print benjaminiHochberg(data)
	
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main())
