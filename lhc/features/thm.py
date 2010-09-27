#!/usr/bin/python

import numpy
import os
import sys
import tempfile
import time

from sequence.rna_tools import RNAFolder
from ushuffle import shuffle
from FileFormats.FastaFile import iterFasta
from string import maketrans

FOLDER = RNAFolder(p=True)

def kshuffle(seq, k=2):
	return shuffle(seq, len(seq), k)

def calcFtrs(seq):
	ftrs = []

	stc, mfe, emfe, cstc, cmfe, cdst, frq, div, bpp = FOLDER.fold(seq)
	
	 # RNAfold features
	ftrs.append(mfe) # Minimum free energy
	ftrs.append(emfe) # Ensemble MFE
	ftrs.append(cmfe) # Centroid MFE
	ftrs.append(cdst) # Centroid distance
	 # F < 0.05
	ftrs.append(frq) # MFE structure frequency in ensemble
	 # F < 0.05
	ftrs.append(div) # Ensemble diversity
	 # F < 0.05
	ftrs.append(entropy(bpp)) # Shannon entropy of base-pairing probabilities
	return ftrs

def entropy(bpp):
	ttl = numpy.empty(bpp.shape[0])
	for i in xrange(bpp.shape[0]):
		ttl[i] = -sum([bpp[i,j] * numpy.log(bpp[i,j]) for j in xrange(i, bpp.shape[1])
		 if bpp[i,j] != 0])
	return numpy.mean([t for t in ttl if t != 0])

def randFtrs(seq, n=1000):
	tmp = calcFtrs(kshuffle(seq))
	ftrs = numpy.empty((n, len(tmp)))
	ftrs[0] = numpy.array(tmp)
	for i in xrange(1, n):
		tmp = calcFtrs(kshuffle(seq))
		ftrs[i] = numpy.array(tmp)
	return ftrs

def nameFtrs():
	ftrs = []
	ftrs.append('Minumum Free Energy')
	ftrs.append('Ensemble MFE')
	ftrs.append('Centroid MFE')
	ftrs.append('Centroid distance')
	ftrs.append('MFE structure frequency in ensemble')
	ftrs.append('Ensemble diversity')
	ftrs.append('Shannon entropy of base-pairing probabilities')
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

