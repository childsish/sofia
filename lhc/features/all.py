#!/usr/bin/python

import numpy
import ushuffle

from optparse import OptionParser
from string import maketrans
from FileFormats.FastaFile import iterFasta

def kshuffle(seq, k=2):
	return ushuffle.shuffle(seq, len(seq), k)

def randFtrs(seq, calcFtrs, n=1000):
	tmp = calcFtrs(kshuffle(seq))
	ftrs = numpy.empty((n, len(tmp)))
	ftrs[0] = numpy.array(tmp)
	for i in xrange(1, n):
		ftrs[i] = numpy.array(calcFtrs(kshuffle(seq)))
	return ftrs

def main(argv):
	trfr = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
	trto = 'atctttgtttttttttttttttttttatctttgttttttttttttttttttt'
	trans = maketrans(trfr, trto)

	# TODO: Use the OptionParser
	
	# Calculate random background
	rnd = '-r' in argv

	# Number of shuffles to generate random background
	if '-n' in argv:
		n = int(argv[argv.index('-n') + 1])
	
	# Feature calculator to use
	if 'seq' in argv:
		import seq as ftr
	elif 'stc' in argv:
		import stc as ftr
	elif 'thm' in argv:
		import thm as ftr
	elif 'ens' in argv:
		import ens as ftr
	elif 'gra_h' in argv:
		import gra_h as ftr
	elif 'gra_s' in argv:
		import gra_s as ftr
	elif 'gen' in argv:
		import gen as ftr
	else:
		raise Exception('No feature calculator selected.')
	
	nams = ftr.nameFtrs()
	sys.stdout.write('class\tid\t')
	sys.stdout.write('\t'.join(nams))
	if rnd:
		sys.stdout.write('\t')
		sys.stdout.write('\t'.join(('%s (rnd)'%nam for nam in nams)))
		sys.stdout.write('\t')
		sys.stdout.write('\t'.join(('%s (z)'%nam for nam in nams)))
	sys.stdout.write('\n')
	
	for hdr, seq in iterFasta(argv[1]):
		seq = seq.translate(trans)
		cls, id_ = hdr.split('_')
		sys.stdout.write('%s\t%s\t'%(cls, id_))
		
		ftrs = ftr.calcFtrs(seq)
		sys.stdout.write('\t'.join(map(str, ftrs)))
		if rnd:
			rnd_ftrs = randFtrs(seq, ftr.calcFtrs, n)
			rnd_avg = numpy.mean(rnd_ftrs, 0)
			rnd_std = numpy.std(rnd_ftrs, 0)
			
			diff = ftrs - rnd_avg
			sys.stdout.write('\t')
			sys.stdout.write('\t'.join(map(str, diff)))
			
			z = diff / rnd_std
			z[numpy.where((diff == 0) & (rnd_std == 0))] = 0
			#z[numpy.where((diff != 0) & (rnd_std == 0))] = 0
			sys.stdout.write('\t')
			sys.stdout.write('\t'.join(map(str, z)))
		sys.stdout.write('\n')
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))

