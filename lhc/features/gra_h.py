#!/usr/bin/python

import igraph
import numpy
import os
import sys
import tempfile

from string import maketrans
from paths.rna import rnadistance
from sequence.rna_tools import RNAFolder
from subprocess import Popen, PIPE
from ushuffle import shuffle
from FileFormats.FastaFile import iterFasta

FOLDER = RNAFolder()

def kshuffle(seq, k=2):
	return shuffle(seq, len(seq), k)

def stc2adj(stc):
	res = numpy.zeros((len(stc), len(stc)), dtype=numpy.float32)
	for i in xrange(len(stc) - 1):
		res[i, i+1] = 1
		res[i+1, i] = 1
	
	stack = []
	for i in xrange(len(stc)):
		if stc[i] == '(':
			stack.append(i)
		elif stc[i] == ')':
			prv = stack.pop()
			cur = i
			res[prv, cur] = 1
			res[cur, prv] = 1
	del stack
	
	return res

def calcFtrs(seq):
	ftrs = []
	
	stc, mfe = FOLDER.fold(seq)
	
	 # Graph features
	adj = stc2adj(stc)
	gra_h = igraph.Graph.Weighted_Adjacency(adj.tolist(), mode=igraph.ADJ_UPPER)
	
	ftrs.append(len(gra_h.articulation_points())) # Number of articulation points
	
	ftrs.append(gra_h.average_path_length()) # Average shortest path length
	
	a = gra_h.betweenness(directed=False)
	#ftrs.append(numpy.mean(a)) # Average vertex betweenness
	 # Linear relation with path length
	#ftrs.append(numpy.std(a)) # Std dev. vertex betweenness
	 # Linear relation with edge betweeness

	a = gra_h.edge_betweenness(directed=False)
	ftrs.append(numpy.mean(a)) # Average edge betweenness
	ftrs.append(numpy.std(a))# Std dev. edge betweenness
	
	#ftrs.append(numpy.mean(gra_h.cocitation())) # Average cocitation distance
	 # Linear relation with graph density
	#ftrs.append(numpy.mean(gra_h.bibcoupling())) # Average bibliographic coupling
	 # Linear relation with graph density
	
	a = gra_h.closeness()
	ftrs.append(numpy.mean(a)) # Average closeness centrality
	ftrs.append(numpy.std(a)) # Std. dev. closeness centrality
	
	a = gra_h.constraint(weights='weight')
	#ftrs.append(numpy.mean(a)) # Average Burt's constraint
	 # Linear relation with graph density
	ftrs.append(numpy.std(a)) # Std. dev. Burt's constraint
	
	#ftrs.append(numpy.mean(gra_h.degree())) # Average degree
	 # Linear relation with graph density
	
	ftrs.append(gra_h.diameter(directed=False)) # Graph diameter

	#ftrs.append(gra_h.girth()) # Graph girth
	 # Always == 4
	
	a = gra_h.coreness()
	ftrs.append(numpy.mean(a)) # Average coreness
	ftrs.append(numpy.std(a)) # Std. dev. coreness
	#ftrs.append(numpy.max(a)) # Maximum coreness
	 # Always == 2
	
	ftrs.append(gra_h.density(True)) # Density

	#ftrs.append(gra_h.transitivity_undirected()) # Transitivity
	 # Always == 0
	
	#a, b = gra_h.authority_score(return_eigenvalue=True)
	#ftrs.append(numpy.mean(a))
	#ftrs.append(numpy.std(a))
	#ftrs.append(b)

	#ftrs.append(gra_h.clique_number()) # Clique number
	 # Always == 2
	#a = gra_h.count_multiple()
	#ftrs.append(numpy.mean(a)) # Average count multiple
	 # Always == 1
	#ftrs.append(numpy.std(a)) # Std. dev. count multiple
	 # Always == 0
	
	#a, b = gra_h.hub_score(return_eigenvalue=True)
	#ftrs.append(numpy.mean(a))
	#ftrs.append(numpy.std(a))
	#ftrs.append(b)

	# Too computationally expensive
	#ftrs.append(gra_h.independence_number())

	ftrs.append(gra_h.mincut_value()) # Mincut
	
	a = gra_h.pagerank()
	#ftrs.append(numpy.mean(a)) # Average page rank
	 # Always 0.005
	ftrs.append(numpy.std(a)) # Std. dev. page rank

	a = gra_h.pagerank_old()
	#ftrs.append(numpy.mean(a)) # Average page rank old
	 # Always 0.005
	ftrs.append(numpy.std(a)) # Std. dev. page rank old
	
	#ftrs.append(gra_h.reciprocity()) # Reciprocity
	 # Always == 1

	a = gra_h.similarity_jaccard()
	ftrs.append(numpy.mean(a)) # Average Jaccard similarity
	ftrs.append(numpy.std(a)) # Std. dev. Jaccard similarity
	
	a = gra_h.community_edge_betweenness(directed=False)
	ftrs.append(len(a)) # Number of edge betweenness communities
	ftrs.append(a.q) # Q of edge betweenness communities
	ftrs.append(numpy.mean(a.sizes())) # Average edge betweenness community size
	ftrs.append(numpy.std(a.sizes())) # Std. dev. edge betweenness community size

	a = gra_h.community_fastgreedy(weights='weight')
	ftrs.append(len(a)) # Number of fast-greedy communities
	ftrs.append(a.q) # Q of fast-greedy communities
	ftrs.append(numpy.mean(a.sizes())) # Average fast-greedy community size
	ftrs.append(numpy.std(a.sizes())) # Std. dev. fast-greedy community size

	#a = gra_h.community_leading_eigenvector()
	#ftrs.append(len(a))
	#ftrs.append(a.q)
	#ftrs.append(numpy.mean(a.sizes()))
	#ftrs.append(numpy.std(a.sizes()))

	#a = gra_h.community_leading_eigenvector_naive()
	#ftrs.append(len(a))
	#ftrs.append(a.q)
	#ftrs.append(numpy.mean(a.sizes()))
	#ftrs.append(numpy.std(a.sizes()))

	a = gra_h.community_walktrap(weights='weight')
	ftrs.append(len(a)) # Number of walktrap communities
	ftrs.append(a.q) # Q of walktrap comminities
	ftrs.append(numpy.mean(a.sizes())) # Average walktrap community size
	ftrs.append(numpy.std(a.sizes())) # Std. dev. walktrap community size

	# Motifs of size 3 and 4. All have low F-scores
	a = gra_h.motifs_randesu(3)
	#ftrs.append(a[0]) # 3-motif 1
	 # Always == 0
	#ftrs.append(a[1]) # 3-motif 2
	 # Always == 0
	ftrs.append(a[2]) # 3-motif 3
	#ftrs.append(a[3]) # 3-motif 4
	 # Always == 0
	a = gra_h.motifs_randesu(4)
	#ftrs.append(a[0]) # 4-motif 1
	 # Always == 0
	#ftrs.append(a[1]) # 4-motif 2
	 # Always == 0
	#ftrs.append(a[2]) # 4-motif 3
	 # Always == 0
	#ftrs.append(a[3]) # 4-motif 4
	 # Always == 0
	ftrs.append(a[4]) # 4-motif 5
	#ftrs.append(a[5]) # 4-motif 6
	 # Always == 0
	ftrs.append(a[6]) # 4-motif 7
	#ftrs.append(a[7]) # 4-motif 8
	 # Always == 0
	ftrs.append(a[8]) # 4-motif 9
	#ftrs.append(a[9]) # 4-motif 10
	 # Always == 0
	#ftrs.append(a[10]) # 4-motif 11
	 # Always == 0
	
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
	ftrs.append('Number of articulation points')
	ftrs.append('Average shortest path length')
	#ftrs.append('Average vertex betweenness')
	#ftrs.append('Std dev. vertex betweenness')
	ftrs.append('Average edge betweenness')
	ftrs.append('Std dev. edge betweenness')
	#ftrs.append('Average cocitation distance')
	#ftrs.append('Average bibliographic coupling')
	ftrs.append('Average closeness centrality')
	ftrs.append('Std. dev. closeness centrality')
	#ftrs.append('Average Burt\'s constraint')
	ftrs.append('Std. dev. Burt\'s constraint')
	#ftrs.append('Average degree')
	ftrs.append('Graph diameter')
	#ftrs.append('Graph girth')
	ftrs.append('Average coreness')
	ftrs.append('Std. dev. coreness')
	#ftrs.append('Maximum coreness')
	ftrs.append('Density')
	#ftrs.append('Transitivity')
	#ftrs.append('Clique number')
	#ftrs.append('Average count multiple')
	#ftrs.append('Std. dev. count multiple')
	ftrs.append('Mincut')
	#ftrs.append('Average page rank')
	ftrs.append('Std. dev. page rank')
	#ftrs.append('Average page rank old')
	ftrs.append('Std. dev. page rank old')
	#ftrs.append('Reciprocity')
	ftrs.append('Average Jaccard similarity')
	ftrs.append('Std. dev. Jaccard similarity')
	ftrs.append('Number of edge betweenness communities')
	ftrs.append('Q of edge betweenness communities')
	ftrs.append('Average edge betweenness community size')
	ftrs.append('Std. dev. edge betweenness community size')
	ftrs.append('Number of fast-greedy communities')
	ftrs.append('Q of fast-greedy communities')
	ftrs.append('Average fast-greedy community size')
	ftrs.append('Std. dev. fast-greedy community size')
	ftrs.append('Number of walktrap communities')
	ftrs.append('Q of walktrap comminities')
	ftrs.append('Average walktrap community size')
	ftrs.append('Std. dev. walktrap community size')
	for i in [2]:
		ftrs.append('3-motif %d'%(i+1))
	for i in [4, 6, 8]:
		ftrs.append('4-motif %d'%(i+1))
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

