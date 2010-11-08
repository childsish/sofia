#!/usr/bin/python 

import numpy
import ushuffle

from string import maketrans
from sequence.rna_tools import RNAFolder
from FileFormats.FastaFile import iterFasta

FOLDER = RNAFolder()

def kshuffle(seq, k=2):
	return ushuffle.shuffle(seq, len(seq), k)

def structuralFeatures(stc):
	hloops = []
	mloops = []
	iloops = []
	bulges = []
	stems = []
	branches = []
	bridges = []
	
	lvls = [[]]
	dots = []
	c_lvl = 0
	c_stem = 0
	for i in xrange(len(stc)):
		if stc[i] == '(':
			if c_lvl == 0:
				bridges.append(len(dots))
				dots = []
			lvls[c_lvl].append('(')
			lvls.append([])
			c_lvl += 1
		elif stc[i] == ')':
			p_lvl = lvls.pop()
			c_lvl -= 1
			
			if p_lvl.count('(') == 0:
				hloops.append(len(p_lvl))
			elif p_lvl.count('(') == 1 and p_lvl.count('.') > 0:
				if p_lvl[0] == '.' and p_lvl[-1] == '.':
					iloops.append((p_lvl.index('('), len(p_lvl) - p_lvl.index('(') - 1))
				else:
					bulges.append(len(p_lvl)-1)
			elif '.' in p_lvl:
				mloops.append(len(p_lvl) - p_lvl.count('('))
				branches.append(p_lvl.count('('))
			
			if p_lvl != ['('] and c_stem != 0:
				stems.append(c_stem)
				c_stem = 0
			c_stem += 1
		elif stc[i] == '.':
			if c_lvl == 0:
				dots.append(i)
			lvls[c_lvl].append('.')
	bridges.append(len(dots))
	stems.append(c_stem)

	return hloops, mloops, iloops, bulges, stems, branches, bridges

def calcFtrs(seq):
	ftrs = []
	stc, mfe = FOLDER.fold(seq)
	a, b, c, d, e, f, g = structuralFeatures(stc)
	 # Hairpin loops - number, total size, average size # F < 0.05
	if len(a) == 0:
		ftrs.extend((0, 0, 0, 0))
	else:
		ftrs.append(len(a)) # Keep (Unshuffled = 0.04)
		ftrs.append(numpy.sum(a))
		ftrs.append(numpy.mean(a))
		ftrs.append(numpy.std(a))
	 # Multi-loops - number, total size, average size # F < 0.05
	if len(b) == 0:
		ftrs.extend((0, 0, 0, 0))
	else:
		ftrs.append(len(b))
		ftrs.append(numpy.sum(b))
		ftrs.append(numpy.mean(b))
		ftrs.append(numpy.std(b))
	 # Internal loops - number, total size, average size, average imbalance
	if len(c) == 0:
		ftrs.extend((0, 0, 0, 0))
	else:
		ftrs.append(len(c))
		ftrs.append(numpy.sum([sum(c_) for c_ in c]))
		ftrs.append(numpy.mean([sum(c_) for c_ in c]))
		ftrs.append(numpy.mean([abs(c_[0] - c_[1]) for c_ in c]))
	 # Bulges - number, total size, average size
	if len(d) == 0:
		ftrs.extend((0, 0, 0, 0))
	else:
		ftrs.append(len(d))
		ftrs.append(numpy.sum(d))
		ftrs.append(numpy.mean(d))
		ftrs.append(numpy.std(d))
	 # Stems - number, total size, average size
	if len(e) == 0:
		ftrs.extend((0, 0, 0, 0))
	else:
		ftrs.append(len(e)) # Keep (Shuffled = 0.04)
		ftrs.append(numpy.sum(e))
		ftrs.append(numpy.mean(e)) # Keep (Shuffled = 0.07)
		ftrs.append(numpy.std(e)) # Keep (Shuffled = 0.07)
	 # Branches - number, total size, average size
	if len(f) == 0:
		ftrs.extend((0, 0, 0, 0))
	else:
		ftrs.append(len(f))
		ftrs.append(numpy.sum(f))
		ftrs.append(numpy.mean(f))
		ftrs.append(numpy.std(f))
	if len(g) == 0:
		ftrs.extend((0, 0, 0, 0))
	else:
		ftrs.append(len(g))
		ftrs.append(numpy.sum(g))
		ftrs.append(numpy.mean(g))
		ftrs.append(numpy.std(g))
	return numpy.array(ftrs)

def randFtrs(seq, n=1000):
	tmp = calcFtrs(kshuffle(seq))
	ftrs = numpy.empty((n, len(tmp)))
	ftrs[0] = numpy.array(tmp)
	for i in xrange(1, n):
		tmp = calcFtrs(kshuffle(seq))
		ftrs[i] = numpy.array(tmp)
	return numpy.mean(ftrs, 0)

def nameFtrs():
	ftrs = []
	ftrs.append('Number of hairpin loops')
	ftrs.append('Total size of hairpins')
	ftrs.append('Average size of hairpins')
	ftrs.append('Stddev of hairpins')
	ftrs.append('Number of multiloops')
	ftrs.append('Total size of multiloops')
	ftrs.append('Average size of multiloops')
	ftrs.append('Stddev of multiloops')
	ftrs.append('Number of internal loops')
	ftrs.append('Total size of internal')
	ftrs.append('Average size of internal')
	ftrs.append('Internal loop imbalance')
	ftrs.append('Number of bulges')
	ftrs.append('Total size of bulges')
	ftrs.append('Average size of bulges')
	ftrs.append('Stddev of bulges')
	ftrs.append('Number of stems')
	ftrs.append('Total size of stems')
	ftrs.append('Average size of stems')
	ftrs.append('Stddev of stems')
	ftrs.append('Number of branches')
	ftrs.append('Total size of branches')
	ftrs.append('Average size of branches')
	ftrs.append('Stddev of bridges')
	ftrs.append('Number of bridges')
	ftrs.append('Total size of bridges')
	ftrs.append('Average size of bridges')
	ftrs.append('Stddev of branches')
	return ftrs

def main(argv):
	rnd = True
	nams = nameFtrs()
	for i in xrange(len(nams)):
		sys.stdout.write('#%d\t%s\n'%(i, nams[i]))
	if rnd:
		for i in xrange(len(nams)):
			sys.stdout.write('#%d\t%s (rnd)\n'%(i + len(nams), nams[i]))
	
	trans = maketrans('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 'atctttgtttttttttttttttttttatctttgttttttttttttttttttt')
	for hdr, seq in iterFasta(argv[1]):
		seq = seq.translate(trans)
		sys.stdout.write('%s\t'%hdr)
		
		ftrs = calcFtrs(seq)
		sys.stdout.write('\t'.join(map(str, ftrs)))
		if rnd:
			sys.stdout.write('\t')
			rnd_ftrs = randFtrs(seq)
			sys.stdout.write('\t'.join(map(str, ftrs - rnd_ftrs)))
		sys.stdout.write('\n')
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
