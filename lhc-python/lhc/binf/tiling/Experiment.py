#!/usr/bin/python

import os
import numpy
import pickle

from FileFormats.affy.CelFile import readCel

class Experiment:
	def __init__(self, tmts, ctls):
		self.tmts = tmts
		self.ctls = ctls
		self.data = None
		for i in xrange(len(tmts)):
			cel = readCel(tmts[i])
			if self.data == None:
				self.data = numpy.empty((len(tmts) + len(ctls), cel.shape[0], cel.shape[1]),\
				 dtype=numpy.float32)
			self.data[i] = cel
		for i in xrange(len(ctls)):
			self.data[len(tmts)+i] = readCel(ctls[i])

def normaliseQuantiles(a):
	""" Warning! Numpy black magic involving fancy indices. """
	# When indexing, y will return the rows.
	y = a.argsort()
	
	# When indexing, z will return the columns (arrays).
	nCol, nRow = a.shape
	x = numpy.ones( (nCol, nRow), dtype=numpy.int32)
	for i in xrange(nCol):
		x[i] *= i
	
	a[x,y] = numpy.median(a[x,y], 0)
	
	del nCol, nRow, x, y

def run(outfname, tmts, ctls):
	data = None
	shape = None
	for i in xrange(len(tmts)):
		cel = readCel(tmts[i])
		if data == None:
			shape = cel.shape
			data = numpy.empty((len(tmts) + len(ctls), shape[0] * shape[1]),\
			 dtype=numpy.float32)
		data[i] = cel.flatten()
	for i in xrange(len(ctls)): 
		cel = readCel(ctls[i])
		data[len(tmts) + i] = cel.flatten()
	
	normaliseQuantiles(data)
	data.shape = (len(data), shape[0], shape[1])
	
	outfile = open(outfname, 'w')
	pickle.dump(tmts, outfile, protocol=pickle.HIGHEST_PROTOCOL)
	pickle.dump(ctls, outfile, protocol=pickle.HIGHEST_PROTOCOL)
	numpy.save(outfile, data)
	outfile.close()

def main(argv):
	outfname = argv[1]
	ctrls = []
	ttmts = []
	for i in xrange(len(argv)):
		if argv[i] == '-c':
			ctrls.append(argv[i+1])
		elif argv[i] == '-t':
			ttmts.append(argv[i+1])
	
	run(outfname, ctrls, ttmts)
	
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
