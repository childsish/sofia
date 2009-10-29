#!/usr/bin/python

from Range import Range, SuperRange

try:
	import psyco
	psyco.full()
except ImportError:
	print 'Unable to import psyco'

def getAcc(parts):
	acc = parts[8]
	if parts[8].startswith('ID='):
		acc = parts[8].split(';')[0][3:]
	elif parts[8].startswith('Parent='):
		acc = parts[8].split(',')[0][7:]
	else:
		raise Exception('No accession found in ' + str(parts))
	return acc

class Feature(Range):
	def __init__(self, fr, to, ann, strand):
		Range.__init__(self, fr, to)
		self.ann = ann
		self.strand = strand
	
	def __str__(self):
		return '%d\t%d\t%s'%(self.f, self.t, self.ann)

class GffFile(dict):
	def __init__(self, fname, cls, chm_idx=0, cls_idx=2, fr_idx=3, to_idx=4, ann_fn=getAcc):
		infile = open(fname)
		for line in infile:
			if line.startswith('#'):
				continue
			
			parts = line.strip().split('\t')
			if parts[cls_idx] == cls:
				ann = ann_fn(parts)
				ftr = Feature(int(parts[fr_idx]), int(parts[to_idx]), ann, parts[6])
				try:
					self[parts[chm_idx]].append(ftr)
				except KeyError:
					self.setdefault(parts[chm_idx], []).append(ftr)
		infile.close()
		for k in self.iterkeys():
			self[k] = sorted(self[k])
	
	def getRange(self, chm, rng):
		ftrs = self[chm]
		idx = binarySearch(ftrs, 0, len(ftrs), rng.f)
		res = []
		while idx < len(ftrs) and ftrs[idx].f <= rng.t:
			if ftrs[idx].t >= rng.f:
				res.append(ftrs[idx])
			idx += 1
		return res
	
	def getHits(self, chm, poss):
		return [self.getRange(chm, Range(pos, pos+1)) for pos in poss]
	
	def merge(self, other):
		for key, vals in other.iteritems():
			if not key in self:
				self[key] = vals
			else:
				self[key] = sorted(set(self[key]) | set(other[key]))

def binarySearch(a, f, t, x):
	""" Specifically for gff ranges."""
	if t - f <= 1:
		return f
	
	m = (f + t) / 2
	if a[m].f < x:
		return binarySearch(a, m, t, x)
	return binarySearch(a, f, m, x)

def main(argv):
	pass

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
