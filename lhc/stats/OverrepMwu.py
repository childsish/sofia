#!/usr/bin/python

# Mann-Whitney U test for Arabidopsis aracyc classification
# Requires a list of gene names and their score (score in first column, name in second).

import sys

from scipy.stats.stats import mannwhitneyu as mwu
from numpy import mean, median

def readAracyc(filename):
	anns = set()
	acc2ann = {}
	
	infile = open(filename)
	infile.readline()
	for line in infile:
		parts = line.strip().split('\t')
		if parts[3][:2].upper() == 'AT' and parts[3][3].upper() == 'G':
			anns.add(parts[0])
			acc2ann.setdefault(parts[3], set()).add(parts[0])
	infile.close()
	return sorted(anns), acc2ann

def calcRanks(acc2scr):
	rnks = {}
	
	# Handle tied accessions
	scrs = {}
	for scr, acc in acc2scr:
		scrs.setdefault(scr, set()).add(acc)
	scrs = sorted(scrs.iteritems())
	
	# Assign a rank to each accession
	for i in xrange(len(scrs)):
		scr, accs = scrs[i]
		for acc in accs:
			rnks[acc] = i
	
	return rnks

def hlestimator(xs, ys):
	res = []
	for x in xs:
		for y in ys:
			res.append(x - y)
	return median(res)

aracyc = '/home/childs/data/lib/Ath/tair/aracyc_dump.20090311'
anns, acc2ann = readAracyc(aracyc)

infile = open(sys.argv[1])
lines = [line.strip().split() for line in infile]
infile.close()

accs = [[float(parts[0]), parts[1]] for parts in lines]
rnks = calcRanks(accs)
del lines

res = []
for ann in anns:
	print ann
	x, y = [], []
	mx, my = [], []
	for i in xrange(len(accs)):
		if ann in acc2ann[accs[i][1]]:
			x.append(accs[i][0])
			mx.append(rnks[accs[i][1]])
		else:
			y.append(accs[i][0])
			my.append(rnks[accs[i][1]])
	
	p = 1
	if len(x) != 0 and len(y) != 0:
		p = mwu(x, y)[1]
	
	res.append((p, ann, len(x), len(y), hlestimator(mx, my)))
res.sort()

outfile = open(sys.argv[2], 'w')
outfile.write('Pathway\tp-value\tIn\tOut\tDifference\n')
outfile.write('\n'.join(['%s\t%.4f\t%d\t%d\t%.1f'%(r[1], r[0], r[2], r[3], r[4]) for r in res]))
outfile.close()
