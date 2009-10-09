#!/usr/bin/python

from IntervalTree import IntervalTree
from Range import Range, SuperRange

try:
	import psyco
	psyco.full()
except ImportError:
	print 'Unable to import psyco'

class Feature(Range):
	def __init__(self, fr, to, chm, cls, acc):
		Range.__init__(self, fr, to)
		self.chm = chm
		self.cls = cls
		self.acc = acc
	
	def __str__(self):
		return '%d\t%d\t%s\t%s'%(self.f, self.t, self.cls, self.acc)

class GffFile:
	def __init__(self, fname):
		# Parse file information
		infile = open(fname)
		genes = [self.__parseParts(line.split('\t')) for line in infile]
		infile.close()
		
		# Insert data into trees
		self.genes = {}
		for gene in genes:
			try:
				self.genes[gene.chm].insert(gene)
			except KeyError:
				self.genes.setdefault(gene.chm, IntervalTree()).insert(gene)
		
		# Delete large and un-needed memory
		del genes
		
		#self.__calculateIntrons()
	
	def __getitem__(self, key):
		return self.genes[key]
	
	def getClass(self, clss, chms=None):
		if chms == None:
			chms = sorted(self.genes.iterkeys())
		
		res = []
		for chm in chms:
			for gene in self.genes[chm]:
				if gene.cls in cls:
					res.append(gene)
		return res
	
	def getRange(self, chm, rngs, labels=None):
		res = []
		if labels == None:
			for rng in rngs:
				res += self.genes[chm].search(rng)
		else:
			for rng in rngs:
				genes = self.genes[chm].search(rng)
				for gene in genes:
					if gene.cls in labels:
						res.append(gene)
		return res
	
	def getHits(self, chm, poss, labels=None):
		rngs = [Range(pos, pos+1) for pos in poss]
		return self.getInRange(chm, rngs, labels)
	
	def getClasses(self, chms = None):
		if chms == None:
			chms = self.genes.iterkeys()
		
		res = set()
		for chm in chms:
			for gene in self.genes[chm]:
				res.add(gene.cls)
		return res
	
	def __parseParts(self, parts):
		acc = parts[8]
		if parts[8].startswith('ID='):
			acc = parts[8].split(';')[0][3:]
		elif parts[8].startswith('Parent='):
			acc = parts[8].split(',')[0][7:]
		else:
			raise Exception('No accession found in ' + str(parts))
		return Feature(int(parts[3])-1, int(parts[4]), parts[0], parts[2], acc)
	
	def __calculateIntrons(self):
		genes = self.get('gene')
		for gene in genes:
			rng = SuperRange([Range(gene.f, gene.t)])
			components = self.genes[gene.chm].search(gene)
			for component in components:
				if component.cls in ['exon', 'five_prime_UTR', 'three_prime_UTR']:
					rng -= component
			for r in rng:
				intron = Feature(gene.chm, r, 'intron', gene.acc)
				self.genes[gene.chm].insert(intron)

def linearSearch(a, f, t, x):
	res = []
	while f < t and a[f].f <= x and a[f].t >= x:
		res.append(f)
		f += 1
	return f

def binarySearch(a, f, t, x):
	""" Specifically for gff ranges."""
	if t - f <= 1:
		return f
	
	m = (f + t) / 2
	if a[m].f < x:
		return binarySearch(a, m, t, x)
	return binarySearch(a, f, m, x)

def getPydName(fname):
	if '.' in fname:
		return '%s.pyd'%(fname[:fname.rfind('.')])
	return '%s.pyd'%(fname)

def readGff(infname):
	import os
	import pickle
	
	indir, fname = os.path.split(infname)
	if os.path.exists(os.path.join(indir, getPydName(fname))):
		infile = open(os.path.join(indir, getPydName(fname)))
		res = pickle.load(infile)
		infile.close()
		return res
	
	gff = GffFile(infname)
	return gff

def pickleGff(infname, outfname=None):
	import os
	import pickle
	
	if outfname == None:
		indir, fname = os.path.split(infname)
		outfname = os.path.join(indir, getPydName(fname))
	if os.path.exists(outfname):
		raise Exception('Pickled file already exists. Delete it if it is out of date.')
	
	res = readGff(infname)
	outfile = open(outfname, 'w')
	pickle.dump(res, outfile, protocol=pickle.HIGHEST_PROTOCOL)
	outfile.close()

def main(argv):
	infile = argv[1]
	outfile = None
	if len(argv) > 2:
		outfile = argv[2]
	pickleGff(infile, outfile)

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
