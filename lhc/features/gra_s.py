#!/usr/bin/python

import igraph
import numpy
import os
import sys

from string import maketrans
from sequence.rna_tools import RNAFolder
from subprocess import Popen, PIPE
from ushuffle import shuffle
from FileFormats.FastaFile import iterFasta

FOLDER = RNAFolder(p=True)

def kshuffle(seq, k=2):
	return shuffle(seq, len(seq), k)

def calcFtrs(seq):
	ftrs = []
	
	stc, mfe, emfe, cstc, cmfe, cdst, frq, div, bpp = FOLDER.fold(seq)
	
	 # Graph features
	bpp = bpp * 10
	gra_s = igraph.Graph.Weighted_Adjacency(bpp.tolist(), mode=igraph.ADJ_UPPER)
	
	ftrs.append(len(gra_s.articulation_points())) # Number of articulation points
	
	ftrs.append(gra_s.average_path_length()) # Average shortest path length
	
	a = gra_s.betweenness(directed=False)
	#ftrs.append(numpy.mean(a)) # Average vertex betweenness
	 # Linear relation with path length
	#ftrs.append(numpy.std(a)) # Std dev. vertex betweenness
	 # Linear relation with edge betweeness

	a = gra_s.edge_betweenness(directed=False)
	ftrs.append(numpy.mean(a)) # Average edge betweenness
	ftrs.append(numpy.std(a))# Std dev. edge betweenness
	
	#ftrs.append(numpy.mean(gra_s.cocitation())) # Average cocitation distance
	 # Linear relation with graph density
	ftrs.append(numpy.mean(gra_s.bibcoupling())) # Average bibliographic coupling
	
	a = gra_s.closeness()
	ftrs.append(numpy.mean(a)) # Average closeness centrality
	ftrs.append(numpy.std(a)) # Std. dev. closeness centrality
	
	a = gra_s.constraint(weights='weight')
	ftrs.append(numpy.mean(a)) # Average Burt's constraint
	ftrs.append(numpy.std(a)) # Std. dev. Burt's constraint
	
	#ftrs.append(numpy.mean(gra_s.degree())) # Average degree
	 # Linear relation with graph density
	
	ftrs.append(gra_s.diameter(directed=False)) # Graph diameter

	#ftrs.append(gra_s.girth()) # Graph girth
	 # Always == 3
	
	a = gra_s.coreness()
	ftrs.append(numpy.mean(a)) # Average coreness
	ftrs.append(numpy.std(a)) # Std. dev. coreness
	ftrs.append(numpy.max(a)) # Maximum coreness
	
	ftrs.append(gra_s.density(True)) # Density

	ftrs.append(gra_s.transitivity_undirected()) # Transitivity
	
	a, b = gra_s.authority_score(return_eigenvalue=True)
	ftrs.append(numpy.mean(a)) # Average authority score
	ftrs.append(numpy.std(a)) # Std. dev. authority score
	ftrs.append(b) # Eigenvalue authority score

	#ftrs.append(gra_s.clique_number()) # Clique number
	 # Always == 4

	#a = gra_s.count_multiple()
	#ftrs.append(numpy.mean(a)) # Average count multiple
	 # Always == 1
	#ftrs.append(numpy.std(a)) # Std. dev. count multiple
	 # Always == 0
	
	a, b = gra_s.hub_score(return_eigenvalue=True)
	ftrs.append(numpy.mean(a)) # Average hub score
	ftrs.append(numpy.std(a)) # Std. dev. hub score
	ftrs.append(b) # Eigenvalue hub score

	# Too computationally expensive
	#ftrs.append(gra_s.independence_number())

	ftrs.append(gra_s.mincut_value()) # Mincut
	
	a = gra_s.pagerank()
	#ftrs.append(numpy.mean(a)) # Average page rank
	 # Always == 0.005
	ftrs.append(numpy.std(a)) # Std. dev. page rank

	a = gra_s.pagerank_old()
	#ftrs.append(numpy.mean(a)) # Average page rank old
	ftrs.append(numpy.std(a)) # Std. dev. page rank old
	
	#ftrs.append(gra_s.reciprocity()) # Reciprocity
	 # Always == 1

	a = gra_s.similarity_jaccard()
	ftrs.append(numpy.mean(a)) # Average Jaccard similarity
	ftrs.append(numpy.std(a)) # Std. dev. Jaccard similarity
	
	# Too computationally expensive
	#a = gra_s.community_edge_betweenness(directed=False)
	#ftrs.append(len(a))
	#ftrs.append(a.q)

	a = gra_s.community_fastgreedy(weights='weight')
	ftrs.append(len(a)) # Number of fast-greedy communities
	ftrs.append(a.q) # Q of fast-greedy communities
	ftrs.append(numpy.mean(a.sizes())) # Average fast-greedy community size
	ftrs.append(numpy.std(a.sizes())) # Std. dev. fast-greedy community size

	# Same as fast greedy
	#a = gra_s.community_leading_eigenvector()
	#ftrs.append(len(a))
	#ftrs.append(a.q)
	#ftrs.append(numpy.mean(a.sizes()))
	#ftrs.append(numpy.std(a.sizes()))

	# Same as fast greedy
	#a = gra_s.community_leading_eigenvector_naive()
	#ftrs.append(len(a))
	#ftrs.append(a.q)
	#ftrs.append(numpy.mean(a.sizes()))
	#ftrs.append(numpy.std(a.sizes()))

	a = gra_s.community_walktrap(weights='weight')
	ftrs.append(len(a)) # Number of walktrap communities
	ftrs.append(a.q) # Q of walktrap comminities
	ftrs.append(numpy.mean(a.sizes())) # Average walktrap community size
	ftrs.append(numpy.std(a.sizes())) # Std. dev. walktrap community size

	# Motifs of size 3 and 4. All have low F-scores
	a = gra_s.motifs_randesu(3)
	#ftrs.append(a[0]) # 3-motif 1
	 # Always == 0
	#ftrs.append(a[1]) # 3-motif 2
	 # Always == 0
	ftrs.append(a[2]) # 3-motif 3
	ftrs.append(a[3]) # 3-motif 4
	a = gra_s.motifs_randesu(4)
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
	ftrs.append(a[7]) # 4-motif 8
	ftrs.append(a[8]) # 4-motif 9
	ftrs.append(a[9]) # 4-motif 10
	ftrs.append(a[10]) # 4-motif 11
	
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
	ftrs.append('Average bibliographic coupling')
	ftrs.append('Average closeness centrality')
	ftrs.append('Std. dev. closeness centrality')
	ftrs.append('Average Burt\'s constraint')
	ftrs.append('Std. dev. Burt\'s constraint')
	#ftrs.append('Average degree')
	ftrs.append('Graph diameter')
	#ftrs.append('Graph girth')
	ftrs.append('Average coreness')
	ftrs.append('Std. dev. coreness')
	ftrs.append('Maximum coreness')
	ftrs.append('Density')
	ftrs.append('Transitivity')
	ftrs.append('Average authority score')
	ftrs.append('Std. dev. authority score')
	ftrs.append('Eigenvalue authority score')
	#ftrs.append('Clique number')
	#ftrs.append('Average count multiple')
	#ftrs.append('Std. dev. count multiple')
	ftrs.append('Average hub score')
	ftrs.append('Std. dev. hub score')
	ftrs.append('Eigenvalue hub score')
	#ftrs.append('Independence number')
	ftrs.append('Mincut')
	#ftrs.append('Average page rank')
	ftrs.append('Std. dev. page rank')
	#ftrs.append('Average page rank old')
	ftrs.append('Std. dev. page rank old')
	#ftrs.append('Reciprocity')
	ftrs.append('Average Jaccard similarity')
	ftrs.append('Std. dev. Jaccard similarity')
	#ftrs.append('Number of edge betweenness communities')
	#ftrs.append('Q of edge betweenness communities')
	ftrs.append('Number of fast-greedy communities')
	ftrs.append('Q of fast-greedy communities')
	ftrs.append('Average fast-greedy community size')
	ftrs.append('Std. dev. fast-greedy community size')
	ftrs.append('Number of walktrap communities')
	ftrs.append('Q of walktrap comminities')
	ftrs.append('Average walktrap community size')
	ftrs.append('Std. dev. walktrap community size')
	for i in [2, 3]:
		ftrs.append('3-motif %d'%(i+1))
	for i in [4, 6, 7, 8, 9, 10]:
		ftrs.append('4-motif %d'%(i+1))
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

