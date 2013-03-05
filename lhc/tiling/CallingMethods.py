import numpy
import random
import pylab
import psyco

from scipy.stats import stats
from scipy.stats.stats import mannwhitneyu as mwu

from PermutationGenerator import PermutationGenerator
from CombinationGenerator import CombinationGenerator

psyco.full()

def normaliseQuantiles(a):
	""" Warning! Numpy black magic involving fancy indices. """
	# When indexing, y will return the rows.
	y = a.argsort()

	# When indexing, z will return the columns (arrays).
	nCol, nRow = a.shape
	x = numpy.ones( (nCol, nRow), dtype=numpy.int32)
	for i in xrange(nCol):
		x[i] *= i

	a[x,y] = numpy.median(a[x,y], 0)
	
	del nCol, nRow, x, y

def foldChange(data, gene, A, B):
	""" A is the control/native state and B the treatment/foreign state. """
	fc = numpy.empty((len(A) * len(B), len(gene)), dtype=numpy.float32)
	for i in xrange(len(gene)):
		for a in xrange(len(A)):
			for b in xrange(len(B)):
				fc[a*len(B)+b, i] = data[A[a],gene[i]] / data[B[b],gene[i]]
	return numpy.median(fc)

def mannwhitneyu(data, gene, A, B):
	if len(gene) == 0:
		return 1.0
	
	try:
		pval = mwu(data[:,gene][A].flatten(), data[:,gene][B].flatten())[1]
	except ValueError, e:
		if e.message == 'All numbers are identical in amannwhitneyu':
			pval = 1.0
		else:
			raise e
	return pval

def ttest(data, gene, A, B):
	pval = stats.ttest_rel(data[A,gene], data[B,gene], 0)[1]
	return pval

def sam(data, gene, T, C):
	uT = numpy.mean(data[T,gene])
	uC = numpy.mean(data[C,gene])
	
	n1 = float(len(T))
	n2 = float(len(C))
	a = (1/n1 + 1/n2) / float(n1 + n2 - 2.)
	s = numpy.sqrt(a *\
		(numpy.sum((numpy.mean(data[T,gene], 1) - uT) ** 2) +\
		numpy.sum((numpy.mean(data[C,gene], 1) - uC) ** 2)))
	so = 3.3 # Check this in the paper.
	
	d = (uT - uC) / (s + so)
	
	return d#, s

#def getCombos(balA, balB, n):
	#""" Assuming that there aren't enough arrays to run a long calculation. """
	#union = set(balA) | set(balB)
	#cmbs = []
	#genA = CombinationGenerator(len(balA), len(balA)/2)
	#for cmbA in genA:
		#genB = CombinationGenerator(len(balB), len(balB)/2)
		#for cmbB in genB:
			#A = set(balA[cmbA]) | set(balB[cmbB])
			#cmbs.append((A, union - A))
	#random.shuffle(cmbs)
	#return sorted(cmbs[:n])

def getCombos(balA, balB, n):
	""" Assuming that there aren't enough arrays to run a long calculation. """
	gen = PermutationGenerator(4)
	cmbs = []
	for cmb in gen:
		cmbs.append((numpy.array([cmb[0], cmb[1]]), numpy.array([cmb[2], cmb[3]])))
	cmbs = [(set([2, 1]), set([0, 3])),
	 (set([0, 3]), set([2, 1])),
	 (set([2, 3]), set([0, 1]))]
	return cmbs

def permute(data, gene, balA, balB, fn):
	cmbs = getCombos(balA, balB, 60)
	
	exps = numpy.empty(len(cmbs), dtype=numpy.float32)
	for i in xrange(len(cmbs)):
		A = numpy.array(list(cmbs[i][0]), dtype=numpy.int32)
		B = numpy.array(list(cmbs[i][1]), dtype=numpy.int32)
		exps[i] = fn(data, gene, A, B)
	
	return numpy.mean(exps)

def expObsDiff(data, gene, A, B, fn):
	obs = fn(data, gene, A, B)
	exp = permute(data, gene, A, B, fn)
	return obs, exp

def main():
	data = numpy.array([[1, 2, 3, 4, 5, 6, 7, 8, 9], [4, 3, 2, 1, 9, 8, 7, 6, 5],
	 [6, 7, 8, 9, 1, 2, 3, 4, 5], [9, 8, 7, 6, 5, 1, 2, 3, 4]], dtype=numpy.float32)
	A = numpy.array([0, 2])
	B = numpy.array([1, 3])
	balA = numpy.array([0, 1])
	balB = numpy.array([2, 3])
	print expObsDiff(data, A, B, balA, balB, foldChange)

if __name__ == '__main__':
	import sys
	sys.exit(main())