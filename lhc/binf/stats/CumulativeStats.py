#!/usr/bin/python

import numpy
import random

class CumulativeStats:
	def __init__(self):
		self.i = 0
		self.avg = 0.
		self.ssq = 0.
	
	def append(self, y):
		newavg = self.avg + (y - self.avg) / (self.i + 1)
		dssq = self.i * (newavg - self.avg) * (newavg - self.avg)
		
		self.avg = newavg
		self.ssq += dssq + (y - newavg) * (y - newavg)
		self.i += 1

	def get(self):
		return self.avg, numpy.sqrt(self.ssq / self.i)

def main(argv):
	x = [5, 1, 7, 6, 3, 8, 3, 4, 1, 3, 7]
	
	cumavg = CumulativeStats()
	for i in xrange(len(x)):
		cumavg.append(x[i])
		print numpy.mean(x[:i+1]), numpy.std(x[:i+1])
		print cumavg.get()
		print
	x = numpy.array(x)
	print numpy.sqrt(sum((x - numpy.mean(x))**2)/float(len(x)))
	
	print cumavg.get()
	print numpy.mean(x), numpy.std(x)

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
