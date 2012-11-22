#!/usr/bin/python

import os
import numpy
import random

class FileFormatError(Exception):
	def __init__(self, msg):
		Exception.__init__(self, msg)

def getNpyName(fname):
	if '.' in fname:
		return '%s.npy'%(fname[:fname.rfind('.')])
	return '%s.npy'%(fname)

def readCel(infname):
	indir, fname = os.path.split(infname)
	if os.path.exists(os.path.join(indir, getNpyName(fname))):
		return numpy.load(os.path.join(indir, getNpyName(fname)))
	
	nrow, ncol = None, None
	infile = open(infname)
	while True:
		line = infile.readline()
		if line.startswith('CellHeader=') or line == '':
			break
		elif line.startswith('Cols='):
			ncol = int(line[5:])
		elif line.startswith('Rows='):
			nrow = int(line[5:])
	
	if nrow == None or ncol == None:
		infile.close()
		raise FileFormatError('Invalid file format: %s'%(infname))
	
	res = numpy.empty((nrow, ncol), dtype=numpy.float32)
	for line in infile:
		try: # Speed hack - Don't have to check for empty line all the time.
			parts = line.split()
			x, y, val = int(parts[0]), int(parts[1]), float(parts[2])
			res[y,x] = val + random.random()
		except ValueError:
			break
		except IndexError:
			break
	infile.close()
	
	return res

def pickleCel(infname, outfname=None):
	if outfname == None:
		indir, fname = os.path.split(infname)
		outfname = os.path.join(indir, getNpyName(fname))
	if os.path.exists(outfname):
		raise Exception('Pickled file already exists. Delete it if it is out of date.')
	
	res = readCel(infname)
	numpy.save(outfname, res)

def main(argv):
	inname = argv[1]
	print inname
	if os.path.isdir(inname):
		for fname in os.listdir(inname):
			print 'Pickling %s'%(fname)
			pickleCel(os.path.join(inname, fname))
	else:
		print 'Pickling %s'%(inname)
		pickleCel(inname)
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
