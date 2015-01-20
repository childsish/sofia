#!/usr/bin/python

import os
import numpy
import pickle

class Chromosome:
	def __init__(self):
		self.pmx = []
		self.pmy = []
		self.mmx = []
		self.mmy = []
		self.pos = []

def getPydName(fname):
	if '.' in fname:
		return '%s.pyd'%(fname[:fname.rfind('.')])
	return '%s.pyd'%(fname)

def readBpmap(infname):
	indir, fname = os.path.split(infname)
	if os.path.exists(os.path.join(indir, getPydName(fname))):
		infile = open(os.path.join(indir, getPydName(fname)))
		res = pickle.load(infile)
		infile.close()
		return res
	
	res = {}
	infile = open(infname)
	infile.readline()
	for line in infile:
		parts = line.split()
		name = parts[4]
		res.setdefault(name, Chromosome())
		res[name].pmx.append(int(parts[0]))
		res[name].pmy.append(int(parts[1]))
		res[name].mmx.append(int(parts[2]))
		res[name].mmy.append(int(parts[3]))
		res[name].pos.append(int(parts[5]))
	for k, v in res.iteritems():
		v.pmx = numpy.array(v.pmx, dtype=numpy.int32)
		v.pmy = numpy.array(v.pmy, dtype=numpy.int32)
		v.mmx = numpy.array(v.mmx, dtype=numpy.int32)
		v.mmy = numpy.array(v.mmy, dtype=numpy.int32)
		v.pos = numpy.array(v.pos, dtype=numpy.int32)
	return res

def pickleBpmap(infname, outfname=None):
	if outfname == None:
		indir, fname = os.path.split(infname)
		outfname = os.path.join(indir, getPydName(fname))
	if os.path.exists(outfname):
		raise Exception('Pickled file already exists. Delete it if it is out of date.')
	
	res = readBpmap(infname)
	outfile = open(outfname, 'w')
	pickle.dump(res, outfile, protocol=pickle.HIGHEST_PROTOCOL)
	outfile.close()

def main(argv):
	infname = sys.argv[1]
	pickleBpmap(infname)
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
