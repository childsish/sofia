#!/usr/bin/python

import time
import random
random.seed(time.time())

from numpy import *
from operator import add

# Improve the speed
try:
	import psyco
	psyco.full()
except ImportError, e:
	print "Unable to import Psyco. Psyco disabled."
	
class BpmapFile:
	def __init__(self, filename):
		import cPickle
		import os.path

		if not os.path.isfile(filename + '.idx'):
			raise 'Index does not exist.'
		
		self.__file = filename
		infile = file(filename + '.idx')
		self.__keys = cPickle.load(infile)
		self.__idxs = cPickle.load(infile)
		self.__counts = cPickle.load(infile)
		infile.close()
	
	def __len__(self):
		total = 0
		for val in self.__counts.itervalues():
			total += val
		return total
	
	def __getitem__(self, key):
		key = self.__findKey(key)
		return BpmapIterator(self.__file, key, self.__idxs[key])
		
	def keys(self):
		return self.__keys
	
	def getLength(self, keys = None):
		if keys == None:
			keys = self.__keys
		elif not isinstance(keys, list):
			keys = [keys]
		
		total = 0
		for key in keys:
			key = self.__findKey(key)
			total += self.__counts[key]
		return total
	
	def getPM(self, cel, keys = None):
		return self.__getSignal(cel, keys, lambda x, y: x.PM(y))
	
	def getPMMM(self, cel, keys = None):
		return self.__getSignal(cel, keys, lambda x, y: x.PMMM(y))
	
	def getMM(self, cel, keys = None):
		return self.__getSignal(cel, keys, lambda x, y: x.MM(y))
	
	def getIntensities(self, cel, keys = None):
		""" I believe it is sufficiently different to __getSignal in concept, if not code, to warrant a seperate function. """
		if keys == None:
			return cel.intensities
		elif not isinstance(keys, list):
			keys = [keys]
		
		intensities = empty(2*self.getLength(keys), dtype=float32)
		i = 0
		for key in keys:
			for probe in self[key]:
				intensities[2*i  ] = probe.PM(cel)
				intensities[2*i+1] = probe.MM(cel)
				i += 1
		
		return intensities
	
	def __getSignal(self, cel, keys, fn):
		if keys == None:
			keys = self.__keys
		elif not isinstance(keys, list):
			keys = [keys]
		
		probes = empty(self.getLength(keys), dtype=float32)
		i = 0
		for key in keys:
			for probe in self[key]:
				probes[i] = fn(probe, cel)
				i += 1
		
		return probes
	
	def __findKey(self, key):
		for key2 in self.__keys:
			if key2.endswith(key):
				return key2
		return key
		

class BpmapEntry:
	def __init__(self, pmx, pmy, mmx, mmy, seq, pos, probe):
		self.pmx = pmx
		self.pmy = pmy
		self.mmx = mmx
		self.mmy = mmy
		self.seq = seq
		self.pos = pos
		self.probe = probe
		self.gc = reduce(add, (x in 'GCgc' for x in self.probe))
	
	def __str__(self):
		return str(self.pmx) + '\t' +\
		       str(self.pmy) + '\t' +\
		       str(self.mmx) + '\t' +\
		       str(self.mmy) + '\t' +\
		       self.seq + '\t' +\
		       str(self.pos) + '\t' +\
		       self.probe
	
	def PM(self, cel):
		return cel[self.pmx + cel.ncol * self.pmy]
	
	def PMMM(self, cel):
		return cel[self.pmx + cel.ncol * self.pmy] - cel[self.mmx + cel.ncol * self.mmy]
	
	def MM(self, cel):
		return cel[self.mmx + cel.ncol * self.mmy]

class BpmapIterator:
	def __init__(self, filename, name, idx):
		self.__file = file(filename)
		self.__file.seek(idx)
		self.__name = name
	
	def __del__(self):
		if not self.__file.closed:
			self.__file.close()
	
	def __iter__(self):
		return self
	
	def next(self):
		if self.__file.closed:
			raise StopIteration()
		
		parts = self.__file.readline().split()
		if len(parts) <= 0 or parts[4] != self.__name:
			self.__file.close()
			raise StopIteration()
		return BpmapEntry(int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]), parts[4], int(parts[5]), parts[6])

class BpmapIndex:
	def __init__(self):
		self.keys = []
		self.idxs = {}
		self.counts = {}

def indexBpmapFile(filename):
	import cPickle
	
	keys = []
	idxs = {}
	counts = {}
	
	infile = file(filename)
	infile.readline()
	prv = None
	idx = infile.tell()
	line = infile.readline()
	count = 0
	while line != '':
		key = line.split()[4]
		
		if key != prv:
			if prv in idxs:
				counts[prv] = count
				count = 0
			
			print key
			keys.append(key)
			idxs[key] = idx
			prv = key
		idx = infile.tell()
		line = infile.readline()
		count += 1
	counts[prv] = count
	infile.close()
	
	outfile = file(filename + '.idx', 'w')
	cPickle.dump(keys, outfile, cPickle.HIGHEST_PROTOCOL)
	cPickle.dump(idxs, outfile, cPickle.HIGHEST_PROTOCOL)
	cPickle.dump(counts, outfile, cPickle.HIGHEST_PROTOCOL)
	outfile.close()

class CelIterator:
	def __init__(self, filename):
		self.__file = file(filename)
		self.__len = 0
		
		self.__parseFile()
	
	def __del__(self):
		if not self.__file.closed:
			self.__file.close()
	
	def __len__(self):
		return self.__len
	
	def __iter__(self):
		return self
	
	def next(self):
		if self.__file.closed:
			raise StopIteration()
		parts = self.__file.readline().split()
		if len(parts) == 0:
			self.__file.close()
			raise StopIteration()
		return float(parts[2])
	
	def __parseFile(self):
		while self.__file.readline().strip() != '[INTENSITY]':
			continue
		self.__len = int(self.__file.readline()[12:])
		self.__file.readline()

class CelFile:
	def __init__(self, filename):
		self.ncol = 0
		self.nrow = 0
		self.intensities = None
		self.outliers = None
		self.__parseFile(filename)
	
	def __len__(self):
		return len(self.intensities)
	
	def __getitem__(self, x):
		if isinstance(x, tuple):
			x = x[0] + self.ncol * x[1]
		return self.intensities[x]
	
	def setOutliers(self, value):
		for outlier in self.outliers:
			self.intensities[outlier] = value
	
	def __parseFile(self, filename):
		infile = file(filename)
		
		line = infile.readline()
		while line != '':
			if line.startswith('Cols='):
				self.ncol = int(line[5:])
			elif line.startswith('Rows='):
				self.nrow = int(line[5:])
			elif line.strip() == '[INTENSITY]':
				self.__parseIntensities(infile)
			elif line.strip() == '[OUTLIERS]':
				#self.__parseOutliers(infile)
				pass # Outliers disabled for now.
			
			line = infile.readline()
		infile.close()
		
		if self.intensities == None or len(self.intensities) == 0:
			raise 'Not a cel file ' + filename
	
	def __parseIntensities(self, infile):
		line = infile.readline()
		self.intensities = empty(int(line[12:]), dtype=float32)
		infile.readline()
		
		line = infile.readline()
		i = 0
		while i < len(self.intensities):
			parts = line.split()
			self.intensities[i] = float(parts[2])
			line = infile.readline()
			i += 1
	
	def __parseOutliers(self, infile):
		line = infile.readline()
		self.outliers = empty(int(line[12:]), dtype=int32)
		line = infile.readline()
		
		line = infile.readline()
		i = 0
		while i < len(self.outliers):
			parts = line.split()
			self.outliers[i] = int(parts[0]) + self.ncol * int(parts[1])
			
			line = infile.readline()
			i += 1

def pm(probe, cel):
	sig = cel.intensities[probe.pmx + cel.ncol * probe.pmy]
	return sig

def pmmm(probe, cel):
	sig = cel.intensities[probe.pmx + cel.ncol * probe.pmy]\
	      - cel.intensities[probe.mmx + cel.ncol * probe.mmy]
	
	if sig < 0:
		sig = 0.0
	return sig

def main(argv = None):
	indexBpmapFile(r"C:\lib\affy\AT3_0001.BPMAP.txt")

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))