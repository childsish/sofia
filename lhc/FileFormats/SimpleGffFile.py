#!/usr/bin/python

from Range import Range, SuperRange

try:
	import psyco
	psyco.full()
except ImportError:
	print 'Unable to import psyco'

class Feature(Range):
	def __init__(self, fr, to, acc):
		Range.__init__(self, fr, to)
		self.acc = acc
	
	def __str__(self):
		return '%d\t%d\t%s\t%s'%(self.f, self.t, self.cls, self.acc)

class GffFile:
	def __init__(self):
		self.ftrs = {}
	
	def __getitem__(self, key):
		return self.ftrs[key]
	
	def getRange(self, chm, rng):
		ftrs = self.ftrs[chm]
		idx = binarySearch(ftrs, 0, len(ftrs), rng.f)
		res = []
		while ftrs[idx].f <= rng.t:
			if ftrs[idx].t >= rng.f:
				res.append(ftrs[idx])
			idx += 1
		return res
	
	def getHits(self, chm, poss):
		return [self.getRange(chm, Range(pos, pos+1)) for pos in poss]
	
	def parseAcc(self, ann):
		acc = ann
		if ann.startswith('ID='):
			acc = ann.split(';')[0][3:]
		elif ann.startswith('Parent='):
			acc = ann.split(',')[0][7:]
		else:
			raise Exception('No accession found in: %s'%(ann))
		return acc

def binarySearch(a, f, t, x):
	""" Specifically for gff ranges."""
	if t - f <= 1:
		return f
	
	m = (f + t) / 2
	if a[m].f < x:
		return binarySearch(a, m, t, x)
	return binarySearch(a, f, m, x)

def readGff(fname, cls):
	gff = GffFile()
	
	infile = open(fname)
	for line in infile:
		parts = line.split()
		if parts[2] == cls:
			acc = gff.parseAcc(parts[8])
			ftr = Feature(int(parts[3]), int(parts[4]), acc)
			try:
				gff[parts[0]].append(ftr)
			except KeyError:
				gff.ftrs.setdefault(parts[0], []).append(ftr)
	infile.close()
	for k in gff.ftrs.iterkeys():
		gff.ftrs[k] = sorted(gff.ftrs[k])
	
	return gff

def main(argv):
	pass

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
