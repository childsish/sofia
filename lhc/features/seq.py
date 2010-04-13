#!/usr/bin/python

import numpy
import ushuffle

from string import maketrans
from FileFormats.FastaFile import iterFasta

def kshuffle(seq, k=2):
	return ushuffle.shuffle(seq, len(seq), k)

def getKmers(k):
	kmers = set()
	bases = 'acgt'
	stk = [[j] for j in bases]
	while len(stk) > 0:
		seq = stk.pop()
		if len(seq) == k:
			kmers.add(''.join(seq))
		else:
			for j in bases:
				cpy = seq[:]
				cpy.append(j)
				stk.append(cpy)
	return kmers

def kContent(seq, k):
	kmers = getKmers(k)
	res = dict([(kmer, 0.) for kmer in kmers])
	for i in xrange(len(seq) - k):
		res[seq[i:i+k]] += 1
	return res

def calcFtrs(seq):
	ftrs = []
	k1mer = kContent(seq, 1)
	k2mer = kContent(seq, 2)
	k3mer = kContent(seq, 3)
	gc = k1mer['g'] + k1mer['c'] / sum(k1mer.itervalues())
	if k1mer['a'] + k1mer['t'] == 0:
		atskew = 0
	else:
		atskew = (k1mer['a'] - k1mer['t']) / (k1mer['a'] + k1mer['t'])
	if k1mer['c'] + k1mer['g'] == 0:
		cgskew = 0
	else:
		cgskew = (k1mer['c'] - k1mer['g']) / (k1mer['c'] + k1mer['g'])
	
	for k, v in sorted(k1mer.iteritems()):
		ftrs.append(v)
	for k, v in sorted(k2mer.iteritems()):
		ftrs.append(v)
	for k, v in sorted(k3mer.iteritems()):
		ftrs.append(v)
	ftrs.append(gc)
	ftrs.append(atskew)
	ftrs.append(cgskew)
	return numpy.array(ftrs)

def randFtrs(seq, n=1000):
	tmp = calcFtrs(kshuffle(seq))
	ftrs = numpy.empty((n, len(tmp)))
	ftrs[0] = numpy.array(tmp)
	for i in xrange(1, n):
		ftrs[i] = numpy.array(calcFtrs(kshuffle(seq)))
	return numpy.mean(ftrs, 0).tolist()

def nameFtrs():
	ftrs = []
	k1mer = getKmers(1)
	k2mer = getKmers(2)
	k3mer = getKmers(3)
	
	for k, v in sorted(k1mer):
		ftrs.append('%s count'%k)
	for k, v in sorted(k2mer):
		ftrs.append('%s count'%k)
	for k, v in sorted(k3mer):
		ftrs.append('%s count'%k)
	ftrs.append('%G+C')
	ftrs.append('AT skew')
	ftrs.append('CG skew')
	return ftrs

def main(argv):
	#nams = nameFtrs()
	#for i in xrange(len(nams)):
	#	print i, nams[i]
	
	trans = maketrans('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 'atctttgtttttttttttttttttttatctttgttttttttttttttttttt')
	for hdr, seq in iterFasta(argv[1]):
		seq = seq.translate(trans)
		ftrs = calcFtrs(seq)
		sys.stdout.write('%s\t'%hdr)
		sys.stdout.write('\t'.join(map(str, ftrs)))
		sys.stdout.write('\t')
		rnd_ftrs = randFtrs(seq)
		sys.stdout.write('\t'.join(map(str, ftrs - rnd_ftrs)))
		sys.stdout.write('\n')

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
