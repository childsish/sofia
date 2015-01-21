#!/usr/bin/python

# Fisher exact test for Arabidopsis aracyc classification
# Requires a list of gene names

import os
import sys
import numpy

from rpy2.robjects import r
from rpy2.robjects import numpy2ri
from MultipleTestCorrection import benjamini_hochberg as correction
#from MultipleTestCorrection import bonferroni as correction

def readAcc2Ann(filename):
	anns = set()
	acc2ann = {}
	
	infile = open(filename)
	infile.readline()
	for line in infile:
		parts = line.strip().split('\t')
		anns.add(parts[1])
		acc2ann.setdefault(parts[0], set()).add(parts[1])
	infile.close()
	return sorted(anns), acc2ann

def readAccs(filename):
	infile = open(filename)
	accs = [line.split()[0] for line in infile]
	infile.close()
	return accs

def makeArray(accs, acc2ann, ann2idx):
	res = numpy.zeros(len(ann2idx), dtype=numpy.int32)
	for acc in accs:
		if acc in acc2ann:
			for ann in acc2ann[acc]:
				res[ann2idx[ann]] += 1
	return res

def test(filename, data, i, ann2idx):
	qry_accs = readAccs(filename)
	all_accs = acc2ann.keys()
	
	all_gens = set(acc2ann.keys())
	
	qry_cnt = makeArray(qry_accs, acc2ann, ann2idx)
	all_cnt = makeArray(all_accs, acc2ann, ann2idx)
	
	res = numpy.empty((len(qry_cnt), 4), dtype=numpy.int32)
	for j in xrange(len(qry_cnt)):
		mat = numpy.array([[qry_cnt[j], sum(qry_cnt) - qry_cnt[j]],
		 [all_cnt[j] - qry_cnt[j], sum(all_cnt) - all_cnt[j] - sum(qry_cnt) + qry_cnt[j]]],
		 dtype=numpy.int32)
		
		p = r['fisher.test'](mat)[0][0] / 2
		
		#print mat, p
		
		data[i,j] = p
		res[j] = mat.flatten()
	return res


anns, acc2ann = readAcc2Ann(sys.argv[2])
ann2idx = dict([(anns[i], i) for i in xrange(len(anns))])
indir = sys.argv[1]

filenames = sorted(os.listdir(indir))
data = numpy.empty((len(filenames), len(anns)), dtype=numpy.float32)
mats = numpy.empty((len(filenames), len(anns), 4), dtype=numpy.int32)
for i in xrange(len(filenames)):
	mats[i] = test(os.path.join(indir, filenames[i]), data, i, ann2idx)

#Find the number of pathways to test against.
res = numpy.empty(len(anns), dtype=numpy.int32)
res[0] = 0
order = numpy.argsort(numpy.min(data, 0))
for i in xrange(1, len(anns)):
	d_ = data[:,order[:i]].flatten()
	r_ = correction(d_)
	res[i] = numpy.sum(r_ <= 0.05)
order = numpy.argsort(res)[::-1]
mxs = []
for i in order:
	if len(mxs) == 0:
		mxs.append(i)
	elif res[i] == res[mxs[-1]]:
		mxs.append(i)
	else:
		break
r['pdf']('tmp.pdf')
r['plot'](numpy.arange(len(res)), res, type='l', xlab='', ylab='')
for mx in mxs:
	fr = mx - 5
	if fr < 0:
		fr = 0
	to = mx + 5
	if to > len(res):
		to = len(res)
	r['plot'](numpy.arange(fr, to), res[fr:to], type='l', xlab='', ylab='')
r['dev.off']()

for mx in mxs:
	outfile = open('annotation.%d.txt'%mx, 'w')
	outfile.write('Case\tPathway\tp-value\t00\t01\t10\t11\n')
	order = numpy.argsort(numpy.min(data, 0))[:mx]
	d_ = correction(data[:,order].flatten())
	d_.shape = (len(filenames), len(order))
	for i in xrange(len(filenames)):
		for j in xrange(len(order)):
			mat = mats[i][order[j]]
			outfile.write('%s\t%s\t%.3e\t%d\t%d\t%d\t%d\n'%\
			(filenames[i], anns[order[j]], d_[i,j], mat[0], mat[1], mat[2], mat[3]))
	outfile.close()
