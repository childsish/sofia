#!/usr/bin/python

import numpy
import os
import sys
import tempfile
import time

from paths.rna import rnadistance, rnafold
from sequence.rna_tools import RNAFolder
from subprocess import Popen, PIPE
from ushuffle import shuffle
from FileFormats.FastaFile import iterFasta
from string import maketrans

ENSEMBLE_SIZE = 1000
FOLDER = RNAFolder()
CWD = tempfile.mkdtemp()

def kshuffle(seq, k=2):
	return shuffle(seq, len(seq), k)

def calcFtrs(seq):
	prps = []

	stc, mfe = FOLDER.fold(seq)
	
	 # Ensemble features
	clus, cpcs, dmat, hibp, hibp_clus, mfe_dsts, bss, wss, bss2, wss2\
	 = ensembleFeatures(seq, stc, mfe)
	prps.append(len(clus)) # Number of clusters in ensemble
	 # F < 0.05
	prps.append(numpy.mean(cpcs)) # Average cluster compactness
	prps.append(numpy.max(cpcs)) # Maximum compactness
	prps.append(numpy.min(cpcs)) # Minimum compactness
	 # F < 0.05
	clu_lens = [len(clu) for clu in clus]
	 # F < 0.05
	prps.append(numpy.max(clu_lens)) # Size of largest cluster
	 # F < 0.05
	prps.append(cpcs[clu_lens.index(numpy.max(clu_lens))]) # Compactness of largest cluster
	 # F < 0.05
	prps.append(numpy.sum(dmat)/2/(ENSEMBLE_SIZE*(ENSEMBLE_SIZE-1))) # Overall compactness
	 # F < 0.05
	prps.append(hibp) # Number of high frequency base-pairs
	 # F < 0.05
	prps.append(numpy.mean(hibp_clus)) # Average cluster hi-freq base-pairs
	 # F < 0.05
	prps.append(numpy.mean(mfe_dsts)) # Average distance of MFE structure to ensemble
	 # F < 0.05
	prps.append(bss) # Between cluster sum of squares (Ding centroid)
	 # F < 0.05
	prps.append(numpy.mean(wss)) # Average within cluster sum of squares (Ding centroid)
	 # F < 0.05
	prps.append(bss2) # Between cluster sum of squares (distance centroid)
	 # F < 0.05
	prps.append(numpy.mean(wss2)) # Average within cluster sum of squares (distance centroid)
	 # F < 0.05

	return prps

def getPairs(stc):
	pairs = []
	stack = []
	for i in xrange(len(stc)):
		if stc[i] == '(':
			stack.append(i)
		elif stc[i] == ')':
			pairs.append((stack.pop(), i))
	return pairs

def ensembleFeatures(seq, stc, mfe):
	from paths.rna import rnasubopt, rnacluster
	
	# Calculate an ensemble of ENSEMBLE_SIZE structures.
	prc = Popen([rnasubopt, '-p', str(ENSEMBLE_SIZE)], stdin=PIPE, stdout=PIPE, cwd=CWD)
	stdout = prc.communicate(seq + '\n')[0]
	efname = os.path.join(CWD, 'ensemble.txt')
	outfile = open(efname, 'w')
	outfile.write(seq + '\n')
	outfile.write(stdout[:-1])
	outfile.close()
	estcs = stdout.split('\n')
	
	# Calculate cluster statistics
	prc = Popen([rnacluster, '-d', '1', '-c', '2', '-minsize', '2', '-i', efname],
	 cwd=CWD, stdout=PIPE)
	prc.wait()
	# Skip the top part of the file
	infile = open(os.path.join(CWD, 'cluster_result.txt'))
	infile.readline()
	line = infile.readline()
	while line[0] != '*':
		line = infile.readline()
	# Parse the clusters
	clus = []
	line = infile.readline()
	while line[0] != '*':
		if line.startswith('Cluster'):
			clus.append(numpy.array([int(part)-1 for part in infile.readline().split()],
			 dtype=numpy.int32))
		line = infile.readline()
	# Skip cluster significance
	line = infile.readline()
	while line[0] != '*':
		line = infile.readline()
	# Parse cluster compactness
	cpcs = []
	line = infile.readline()
	while line[0] != '*':
		if line.startswith('cluster'):
			cpcs.append(float(line.split()[-1]))
		line = infile.readline()
	infile.close()
	
	# Calculate the distance matrix
	dmat = getDistanceMatrix(efname)
	
	# Calculate number of high frequency base-pairs per cluster and ensemble
	thr_hifrq = 0.5
	ecnt_d = getCentroidDing(estcs, thr_hifrq)
	cnt_ds = [getCentroidDing([estcs[idx] for idx in clus[i]], thr_hifrq)
	 for i in xrange(len(clus))]
	hibp_clus = [cnt.count('(') for cnt in cnt_ds]
	hibp = ecnt_d.count('(')
	
	# Calculate MFE structure distance to ensemble
	mfe_dsts = getDistanceArray(seq, stc, estcs)
	
	# Calculate between/within cluster sum of squares
	bss = getStructureSumOfSquares(seq, ecnt_d, cnt_ds)
	wss = [getStructureSumOfSquares(seq, cnt_ds[i], [estcs[j] for j in clus[i]])
	 for i in xrange(len(clus))]
	
	# Get centroids and calculate between/within cluster sum of squares
	ecnt_p = getCentroid(estcs, dmat)
	cnt_ps = [getCentroid([estcs[idx] for idx in clus[i]], dmat[clus[i]][:,clus[i]])
	 for i in xrange(len(clus))]
	bss2 = getStructureSumOfSquares(seq, ecnt_p, cnt_ps)
	wss2 = [getStructureSumOfSquares(seq, cnt_ps[i], [estcs[j] for j in clus[i]])
	 for i in xrange(len(clus))]
	
	return clus, cpcs, dmat, hibp, hibp_clus, mfe_dsts, bss, wss, bss2, wss2
	#return cpcs

def getStructureSumOfSquares(seq, cnt, stcs):
	dsts = getDistanceArray(seq, cnt, stcs)
	return numpy.sum(dsts*dsts)/len(dsts)

def getCentroidDing(stcs, thr):
	pairs = {}
	for stc in stcs:
		for pair in getPairs(stc):
			pairs.setdefault(pair, 0)
			pairs[pair] += 1
	res = ['.' for i in xrange(len(stcs[0]))]
	for k, v in pairs.iteritems():
		if v/float(len(stcs)) > thr:
			res[k[0]] = '('
			res[k[1]] = ')'
	return ''.join(res)

def getCentroid(stcs, dmat):
	return stcs[numpy.argsort(numpy.sum(dmat, 1))[0]]

def getDistanceMatrix(fname):
	prc_stdin = open(fname)
	prc = Popen([rnadistance, '-DP', '-Xm'], stdin=prc_stdin, stdout=PIPE)
	prc.stdout.readline()
	res = numpy.zeros((ENSEMBLE_SIZE, ENSEMBLE_SIZE))
	i = 0
	for line in prc.stdout:
		parts = line.split()
		for j in xrange(len(parts)):
			res[i+1,j] = int(parts[j])
			res[j,i+1] = int(parts[j])
		i += 1
	return res

def getDistanceArray(seq, stc, stcs):
	prc = Popen([rnadistance, '-DP', '-Xf'], stdin=PIPE, stdout=PIPE)
	prc.stdin.write(seq)
	prc.stdin.write('\n')
	prc.stdin.write(stc)
	prc.stdin.write('\n')
	prc.stdin.write('\n'.join(stcs))
	prc.stdin.write('\n')
	lines = prc.communicate()[0].split('\n')
	res = numpy.array([int(line.split()[1]) for line in lines if line != ''])
	return res

def randFtrs(seq, n=1000):
	prps = None
	for i in xrange(n):
		rseq = kshuffle(seq)
		rprp = calcFtrs(rseq)
		if prps == None:
			prps = [[] for j in xrange(len(rprp))]
		for j in xrange(len(rprp)):
			prps[j].append(rprp[j])
	for i in xrange(len(prps)):
		prps[i] = numpy.mean(prps[i])
	return numpy.array(prps)

def nameFtrs():
	ftrs = []
	ftrs.append('Number of ensemble clusters')
	ftrs.append('Average cluster compactness')
	ftrs.append('Maximum compactness')
	ftrs.append('Minimum compactness')
	ftrs.append('Size of largest cluster')
	ftrs.append('Compactness of largest cluster')
	ftrs.append('Overall compactness')
	ftrs.append('Number of hi freq base-pairs')
	ftrs.append('Average cluster hi freq base-pairs')
	ftrs.append('Average distance MFE to ensemble')
	ftrs.append('Between cluster SS (Ding centroid)')
	ftrs.append('Within cluster SS (Ding centroid)')
	ftrs.append('Between cluster SS (distance centroid)')
	ftrs.append('Within cluster SS (distance centroid)')
	return ftrs

def main(argv):
	rnd = False
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

