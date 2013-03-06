#!/usr/bin/python

import numpy

from paths.svms import mfeavg200, mfestd200, efeavg200, efestd200
from sequence.rna_tools import RNAFolder
from sequence.seq_tools import kContent
from libsvm import svmutil

FOLDER = RNAFolder(p=True)

def loadRange(fname):
	avgs = []
	stds = []
	infile = open(fname)
	for line in infile:
		avg, std = line.strip().split()
		avgs.append(avg)
		stds.append(std)
	infile.close()
	
	return numpy.array(avgs, dtype=numpy.float32), numpy.array(stds, dtype=numpy.float32)

def calcFtrs(seq):
	ftrs = []
	
	stc, mfe, efe, cstc, cmfe, cdst, frq, div, bpp = FOLDER.fold(seq)
	
	kmer = kContent(seq, 1)
	atcg = (kmer['a'] + kmer['t']) / (kmer['a'] + kmer['t'] + kmer['c'] + kmer['g'])
	if kmer['a'] + kmer['t'] == 0:
		at = 0
	else:
		at = kmer['a'] / (kmer['a'] + kmer['t'])
	if kmer['c'] + kmer['g'] == 0:
		cg = 0
	else:
		cg = kmer['c'] / (kmer['c'] + kmer['g'])
	
	svmftrs = numpy.array((atcg, at, cg))
	
	mfeavg_mdl = svmutil.svm_load_model(mfeavg200)
	mfestd_mdl = svmutil.svm_load_model(mfestd200)
	efeavg_mdl = svmutil.svm_load_model(efeavg200)
	#efestd_mdl = svmutil.svm_load_model(efestd200)
	
	mfeavg_avg, mfeavg_std = loadRange(mfeavg200 + '.rng')
	mfestd_avg, mfestd_std = loadRange(mfestd200 + '.rng')
	efeavg_avg, efeavg_std = loadRange(efeavg200 + '.rng')
	#efestd_avg, efestd_std = loadRange(efestd200 + '.rng')
	
	mfe_avg = svmutil.svm_predict([0],
	 [((svmftrs - mfeavg_avg) / mfeavg_std).tolist()], mfeavg_mdl, options='-b 1')[0][0]
	mfe_std = svmutil.svm_predict([0],
	 [((svmftrs - mfestd_avg) / mfestd_std).tolist()], mfestd_mdl, options='-b 1')[0][0]
	efe_avg = svmutil.svm_predict([0],
	 [((svmftrs - efeavg_avg) / efeavg_std).tolist()], efeavg_mdl, options='-b 1')[0][0]
	#efe_std = svmutil.svm_predict([0],
	# [((svmftrs - efestd_avg) / efestd_std).tolist()], efestd_mdl, options='-b 1')[0][0]
	
	ftrs.append(mfe - mfe_avg)
	ftrs.append((mfe - mfe_avg) / mfe_std)
	ftrs.append(efe - efe_avg)
	#ftrs.append((efe - efe_avg) / efe_std)
	
	return numpy.array(ftrs)

def nameFtrs():
	ftrs = []
	ftrs.append('Generated MFE')
	ftrs.append('Generated MFEz')
	ftrs.append('Generated EFE')
	#ftrs.append('Generated EFEz')
	return ftrs

def main(argv):
	from Bio import SeqIO
	outfile = open(argv[2], 'w')
	outfile.write('\t'.join(nameFtrs()))
	outfile.write('\n')
	for ent in SeqIO.parse(argv[1], 'fasta'):
		outfile.write('\t'.join('%.3f'%ftr for ftr in calcFtrs(str(ent.seq))))
		outfile.write('\n')
	outfile.close()

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))