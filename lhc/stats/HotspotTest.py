#!/usr/bin/python

import numpy
import random

from scipy.stats.stats import mannwhitneyu as mwu

PLOT = False
if PLOT:
	from rpy2.robjects import r
	from rpy2.robjects import numpy2ri
	from numpy import histogram

def plot(obs_dsts, rnd_dsts, n):
	mn = min(min(obs_dsts), min(rnd_dsts))
	mx = max(max(obs_dsts), max(rnd_dsts))
	bins = numpy.arange(mn, mx, (mx-mn)/100.)
	
	h1, e1 = histogram(obs_dsts, bins)
	h2, e2 = histogram(rnd_dsts, bins)
	
	r['pdf']('cluster_test.pdf')
	r['plot'](bins[1:], h1, type='l', col=1, xlab='', ylab='')
	r['points'](bins[1:], h2/n, type='l', col=2)
	r['dev.off']()

def readFile(fname):
	infile = open(fname)
	poss = [int(line) for line in infile]
	infile.close()
	return poss

def dist(poss):
	res = (len(poss)-1) * [None]
	poss.sort()
	for i in xrange(len(poss)):
		res[i-1] = poss[i] - poss[i-1]
	return res

def test(obss, vlds, n):
	obs_dsts = dist(obss)
	rnd_dsts = []
	for i in xrange(n):
		rnds = random.sample(vlds, len(obss))
		rnd_dsts += dist(rnds)
	
	if PLOT:
		plot(numpy.array(obs_dsts), numpy.array(rnd_dsts), n)
	
	return mwu(obs_dsts, rnd_dsts)[1], numpy.mean(obs_dsts) - numpy.mean(rnd_dsts)

def multiTest(obss, vlds, n):
	obs_dsts = []
	for obs in obss:
		obs_dsts += dist(obs)
	
	rnd_dsts = []
	for i in xrange(n):
		for i in xrange(len(obss)):
			rnds = random.sample(vlds[i], len(obss[i]))
			rnd_dsts += dist(rnds)
	
	return mwu(obs_dsts, rnd_dsts)[1], numpy.mean(obs_dsts) - numpy.mean(rnd_dsts)

def run(obsfname, validfname, n):
	obss = readFile(obsfname)
	vlds = readFile(validfname)
	
	return test(obss, vlds)

def main(argv):
	vlds = numpy.array(range(200) + range(500, 700))
	obss = random.sample(range(200), 30) +\
	 random.sample(range(500, 700), 70)
	print test(obss, vlds, 1000)
	return 0
	
	print run(argv[1], argv[2], int(argv[3]))
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))