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

FOLDER = RNAFolder(p=True)

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
	
	stc, mfe, emfe, cstc, cmfe, cdst, frq, div, bpp = FOLDER.fold(seq)
	
	 # Graph features
	adj = stc2adj(stc)
	for i in xrange(1, len(seq)):
		bpp[i-1,i] = 1
		bpp[i,i-1] = 1
	gra_h = igraph.Graph.Weighted_Adjacency(adj.tolist(), mode=igraph.ADJ_UPPER)
	gra_s = igraph.Graph.Weighted_Adjacency(bpp.tolist(), mode=igraph.ADJ_UPPER)
	
	ftrs.append(len(gra_h.articulation_points())) # Number of articulation points (hard)
	ftrs.append(len(gra_s.articulation_points())) # Number of articulation points (soft)
	
	ftrs.append(gra_h.average_path_length()) # Average shortest path length (hard)
	ftrs.append(gra_s.average_path_length()) # Average shortest path length (soft)
	
	a = gra_h.betweenness(directed=False)
	ftrs.append(numpy.mean(a)) # Average vertex betweenness (hard)
	 # Linear relation with path length (hard)
	ftrs.append(numpy.std(a)) # Std dev. vertex betweenness (hard)
	 # Linear relation with edge betweeness (hard)
	a = gra_s.betweenness(directed=False)
	ftrs.append(numpy.mean(a)) # Average vertex betweenness (soft)
	 # Linear relation with path length (soft)
	ftrs.append(numpy.std(a)) # Std dev. vertex betweenness (soft)
	 # Linear relation with edge betweeness (soft)

	a = gra_h.edge_betweenness(directed=False)
	ftrs.append(numpy.mean(a)) # Average edge betweenness (hard)
	ftrs.append(numpy.std(a))# Std dev. edge betweenness (hard)
	a = gra_s.edge_betweenness(directed=False)
	ftrs.append(numpy.mean(a)) # Average edge betweenness (soft)
	ftrs.append(numpy.std(a))# Std dev. edge betweenness (soft)
	
	ftrs.append(numpy.mean(gra_h.cocitation())) # Average cocitation distance (hard)
	 # Linear relation with graph density
	ftrs.append(numpy.mean(gra_s.cocitation())) # Average cocitation distance (soft)
	ftrs.append(numpy.mean(gra_h.bibcoupling())) # Average bibliographic coupling (hard)
	 # Linear relation with graph density
	ftrs.append(numpy.mean(gra_s.bibcoupling())) # Average bibliographic coupling (soft)
	
	a = gra_h.closeness()
	ftrs.append(numpy.mean(a)) # Average closeness centrality (hard)
	ftrs.append(numpy.std(a)) # Std. dev. closeness centrality (hard)
	a = gra_s.closeness()
	ftrs.append(numpy.mean(a)) # Average closeness centrality (soft)
	ftrs.append(numpy.std(a)) # Std. dev. closeness centrality (soft)
	
	a = gra_h.constraint(weights='weight')
	ftrs.append(numpy.mean(a)) # Average Burt's constraint (hard)
	 # Linear relation with graph density
	ftrs.append(numpy.std(a)) # Std. dev. Burt's constraint (hard)
	a = gra_s.constraint(weights='weight')
	ftrs.append(numpy.mean(a)) # Average Burt's constraint (soft)
	ftrs.append(numpy.std(a)) # Std. dev. Burt's constraint (soft)
	
	ftrs.append(numpy.mean(gra_h.degree())) # Average degree (hard)
	 # Linear relation with graph density
	ftrs.append(numpy.mean(gra_s.degree())) # Average degree (soft)
	 # Linear relation with graph density
	
	ftrs.append(gra_h.diameter(directed=False)) # Graph diameter (hard)
	ftrs.append(gra_s.diameter(directed=False)) # Graph diameter (soft)

	#ftrs.append(gra_h.girth()) # Graph girth (hard)
	 # Always == 4
	#ftrs.append(gra_s.girth()) # Graph girth (soft)
	 # Always == 3
	
	a = gra_h.coreness()
	ftrs.append(numpy.mean(a)) # Average coreness (hard)
	ftrs.append(numpy.std(a)) # Std. dev. coreness (hard)
	#ftrs.append(numpy.max(a)) # Maximum coreness (hard)
	 # Always == 2
	a = gra_s.coreness()
	ftrs.append(numpy.mean(a)) # Average coreness (soft)
	ftrs.append(numpy.std(a)) # Std. dev. coreness (soft)
	ftrs.append(numpy.max(a)) # Maximum coreness (soft)
	
	ftrs.append(gra_h.density(True)) # Density (hard)
	ftrs.append(gra_s.density(True)) # Density (soft)

	#ftrs.append(gra_h.transitivity_undirected()) # Transitivity (hard)
	 # Always == 0
	ftrs.append(gra_s.transitivity_undirected()) # Transitivity (soft)
	
	#a, b = gra_h.authority_score(return_eigenvalue=True)
	#ftrs.append(numpy.mean(a))
	#ftrs.append(numpy.std(a))
	#ftrs.append(b)
	a, b = gra_s.authority_score(return_eigenvalue=True)
	ftrs.append(numpy.mean(a)) # Average authority score (soft)
	ftrs.append(numpy.std(a)) # Std. dev. authority score (soft)
	ftrs.append(b) # Eigenvalue authority score (soft)

	#ftrs.append(gra_h.clique_number()) # Clique number (hard)
	 # Always == 2
	#ftrs.append(gra_s.clique_number()) # Clique number (soft)
	 # Always == 4

	#a = gra_h.count_multiple()
	#ftrs.append(numpy.mean(a)) # Average count multiple (hard)
	 # Always == 1
	#ftrs.append(numpy.std(a)) # Std. dev. count multiple (hard)
	 # Always == 0
	#a = gra_s.count_multiple()
	#ftrs.append(numpy.mean(a)) # Average count multiple (soft)
	 # Always == 1
	#ftrs.append(numpy.std(a)) # Std. dev. count multiple (soft)
	 # Always == 0
	
	#a, b = gra_h.hub_score(return_eigenvalue=True)
	#ftrs.append(numpy.mean(a))
	#ftrs.append(numpy.std(a))
	#ftrs.append(b)
	a, b = gra_s.hub_score(return_eigenvalue=True)
	ftrs.append(numpy.mean(a)) # Average hub score (soft)
	ftrs.append(numpy.std(a)) # Std. dev. hub score (soft)
	ftrs.append(b) # Eigenvalue hub score (soft)

	# Too computationally expensive
	#ftrs.append(gra_h.independence_number())
	#ftrs.append(gra_s.independence_number())

	ftrs.append(gra_h.mincut_value()) # Mincut (hard)
	ftrs.append(gra_s.mincut_value()) # Mincut (soft)
	
	a = gra_h.pagerank()
	#ftrs.append(numpy.mean(a)) # Average page rank (hard)
	ftrs.append(numpy.std(a)) # Std. dev. page rank (hard)
	a = gra_s.pagerank()
	#ftrs.append(numpy.mean(a)) # Average page rank (soft)
	ftrs.append(numpy.std(a)) # Std. dev. page rank (soft)

	a = gra_h.pagerank_old()
	#ftrs.append(numpy.mean(a)) # Average page rank old (hard)
	ftrs.append(numpy.std(a)) # Std. dev. page rank old (hard)
	a = gra_s.pagerank_old()
	#ftrs.append(numpy.mean(a)) # Average page rank old (soft)
	ftrs.append(numpy.std(a)) # Std. dev. page rank old (soft)
	
	#ftrs.append(gra_h.reciprocity()) # Reciprocity (hard)
	 # Always == 1
	#ftrs.append(gra_s.reciprocity()) # Reciprocity (soft)
	 # Always == 1

	a = gra_h.similarity_jaccard()
	ftrs.append(numpy.mean(a)) # Average Jaccard similarity (hard)
	ftrs.append(numpy.std(a)) # Std. dev. Jaccard similarity (hard)
	a = gra_s.similarity_jaccard()
	ftrs.append(numpy.mean(a)) # Average Jaccard similarity (soft)
	ftrs.append(numpy.std(a)) # Std. dev. Jaccard similarity (soft)
	
	a = gra_h.community_edge_betweenness(directed=False)
	ftrs.append(len(a)) # Number of edge betweenness communities (hard)
	ftrs.append(a.q) # Q of edge betweenness communities (hard)
	ftrs.append(numpy.mean(a.sizes())) # Average edge betweenness community size (hard)
	ftrs.append(numpy.std(a.sizes())) # Std. dev. edge betweenness community size (hard)
	# Too computationally expensive
	#a = gra_s.community_edge_betweenness(directed=False)
	#ftrs.append(len(a))
	#ftrs.append(a.q)

	a = gra_h.community_fastgreedy(weights='weight')
	ftrs.append(len(a)) # Number of fast-greedy communities (hard)
	ftrs.append(a.q) # Q of fast-greedy communities (hard)
	ftrs.append(numpy.mean(a.sizes())) # Average fast-greedy community size (hard)
	ftrs.append(numpy.std(a.sizes())) # Std. dev. fast-greedy community size (hard)
	a = gra_s.community_fastgreedy(weights='weight')
	ftrs.append(len(a)) # Number of fast-greedy communities (soft)
	ftrs.append(a.q) # Q of fast-greedy communities (soft)
	ftrs.append(numpy.mean(a.sizes())) # Average fast-greedy community size (soft)
	ftrs.append(numpy.std(a.sizes())) # Std. dev. fast-greedy community size (soft)

	#a = gra_h.community_leading_eigenvector()
	#ftrs.append(len(a))
	#ftrs.append(a.q)
	#ftrs.append(numpy.mean(a.sizes()))
	#ftrs.append(numpy.std(a.sizes()))
	#a = gra_s.community_leading_eigenvector()
	#ftrs.append(len(a))
	#ftrs.append(a.q)
	#ftrs.append(numpy.mean(a.sizes()))
	#ftrs.append(numpy.std(a.sizes()))

	#a = gra_h.community_leading_eigenvector_naive()
	#ftrs.append(len(a))
	#ftrs.append(a.q)
	#ftrs.append(numpy.mean(a.sizes()))
	#ftrs.append(numpy.std(a.sizes()))
	#a = gra_s.community_leading_eigenvector_naive()
	#ftrs.append(len(a))
	#ftrs.append(a.q)
	#ftrs.append(numpy.mean(a.sizes()))
	#ftrs.append(numpy.std(a.sizes()))

	a = gra_h.community_walktrap(weights='weight')
	ftrs.append(len(a)) # Number of walktrap communities (hard)
	ftrs.append(a.q) # Q of walktrap comminities (hard)
	ftrs.append(numpy.mean(a.sizes())) # Average walktrap community size (hard)
	ftrs.append(numpy.std(a.sizes())) # Std. dev. walktrap community size (hard)
	a = gra_s.community_walktrap(weights='weight')
	ftrs.append(len(a)) # Number of walktrap communities (soft)
	ftrs.append(a.q) # Q of walktrap comminities (soft)
	ftrs.append(numpy.mean(a.sizes())) # Average walktrap community size (soft)
	ftrs.append(numpy.std(a.sizes())) # Std. dev. walktrap community size (soft)

	# Motifs of size 3 and 4. All have low F-scores
	a = gra_h.motifs_randesu(3)
	#ftrs.append(a[0]) # 3-motif 1 (hard)
	 # Always == 0
	#ftrs.append(a[1]) # 3-motif 2 (hard)
	 # Always == 0
	ftrs.append(a[2]) # 3-motif 3 (hard)
	#ftrs.append(a[3]) # 3-motif 4 (hard)
	 # Always == 0
	a = gra_h.motifs_randesu(4)
	#ftrs.append(a[0]) # 4-motif 1 (hard)
	 # Always == 0
	#ftrs.append(a[1]) # 4-motif 2 (hard)
	 # Always == 0
	#ftrs.append(a[2]) # 4-motif 3 (hard)
	 # Always == 0
	#ftrs.append(a[3]) # 4-motif 4 (hard)
	 # Always == 0
	ftrs.append(a[4]) # 4-motif 5 (hard)
	#ftrs.append(a[5]) # 4-motif 6 (hard)
	 # Always == 0
	ftrs.append(a[6]) # 4-motif 7 (hard)
	#ftrs.append(a[7]) # 4-motif 8 (hard)
	 # Always == 0
	ftrs.append(a[8]) # 4-motif 9 (hard)
	#ftrs.append(a[9]) # 4-motif 10 (hard)
	 # Always == 0
	#ftrs.append(a[10]) # 4-motif 11 (hard)
	 # Always == 0
	a = gra_s.motifs_randesu(3)
	#ftrs.append(a[0]) # 3-motif 1 (soft)
	 # Always == 0
	#ftrs.append(a[1]) # 3-motif 2 (soft)
	 # Always == 0
	ftrs.append(a[2]) # 3-motif 3 (soft)
	ftrs.append(a[3]) # 3-motif 4 (soft)
	a = gra_s.motifs_randesu(4)
	#ftrs.append(a[0]) # 4-motif 1 (soft)
	 # Always == 0
	#ftrs.append(a[1]) # 4-motif 2 (soft)
	 # Always == 0
	#ftrs.append(a[2]) # 4-motif 3 (soft)
	 # Always == 0
	#ftrs.append(a[3]) # 4-motif 4 (soft)
	 # Always == 0
	ftrs.append(a[4]) # 4-motif 5 (soft)
	#ftrs.append(a[5]) # 4-motif 6 (soft)
	 # Always == 0
	ftrs.append(a[6]) # 4-motif 7 (soft)
	ftrs.append(a[7]) # 4-motif 8 (soft)
	ftrs.append(a[8]) # 4-motif 9 (soft)
	ftrs.append(a[9]) # 4-motif 10 (soft)
	ftrs.append(a[10]) # 4-motif 11 (soft)
	
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
	ftrs.append('Number of articulation points (hard)')
	ftrs.append('Number of articulation points (soft)')
	ftrs.append('Average shortest path length (hard)')
	ftrs.append('Average shortest path length (soft)')
	ftrs.append('Average vertex betweenness (hard)')
	ftrs.append('Std dev. vertex betweenness (hard)')
	ftrs.append('Average vertex betweenness (soft)')
	ftrs.append('Std dev. vertex betweenness (soft)')
	ftrs.append('Average edge betweenness (hard)')
	ftrs.append('Std dev. edge betweenness (hard)')
	ftrs.append('Average edge betweenness (soft)')
	ftrs.append('Std dev. edge betweenness (soft)')
	ftrs.append('Average cocitation distance (hard)')
	ftrs.append('Average cocitation distance (soft)')
	ftrs.append('Average bibliographic coupling (hard)')
	ftrs.append('Average bibliographic coupling (soft)')
	ftrs.append('Average closeness centrality (hard)')
	ftrs.append('Std. dev. closeness centrality (hard)')
	ftrs.append('Average closeness centrality (soft)')
	ftrs.append('Std. dev. closeness centrality (soft)')
	ftrs.append('Average Burt\'s constraint (hard)')
	ftrs.append('Std. dev. Burt\'s constraint (hard)')
	ftrs.append('Average Burt\'s constraint (soft)')
	ftrs.append('Std. dev. Burt\'s constraint (soft)')
	ftrs.append('Average degree (hard)')
	ftrs.append('Average degree (soft)')
	ftrs.append('Graph diameter (hard)')
	ftrs.append('Graph diameter (soft)')
	#ftrs.append('Graph girth (hard)')
	#ftrs.append('Graph girth (soft)')
	ftrs.append('Average coreness (hard)')
	ftrs.append('Std. dev. coreness (hard)')
	#ftrs.append('Maximum coreness (hard)')
	ftrs.append('Average coreness (soft)')
	ftrs.append('Std. dev. coreness (soft)')
	ftrs.append('Maximum coreness (soft)')
	ftrs.append('Density (hard)')
	ftrs.append('Density (soft)')
	#ftrs.append('Transitivity (hard)')
	ftrs.append('Transitivity (soft)')
	ftrs.append('Average authority score (soft)')
	ftrs.append('Std. dev. authority score (soft)')
	ftrs.append('Eigenvalue authority score (soft)')
	#ftrs.append('Clique number (hard)')
	#ftrs.append('Clique number (soft)')
	#ftrs.append('Average count multiple (hard)')
	#ftrs.append('Std. dev. count multiple (hard)')
	#ftrs.append('Average count multiple (soft)')
	#ftrs.append('Std. dev. count multiple (soft)')
	ftrs.append('Average hub score (soft)')
	ftrs.append('Std. dev. hub score (soft)')
	ftrs.append('Eigenvalue hub score (soft)')
	ftrs.append('Mincut (hard)')
	ftrs.append('Mincut (soft)')
	#ftrs.append('Average page rank (hard)')
	ftrs.append('Std. dev. page rank (hard)')
	#ftrs.append('Average page rank (soft)')
	ftrs.append('Std. dev. page rank (soft)')
	#ftrs.append('Average page rank old (hard)')
	ftrs.append('Std. dev. page rank old (hard)')
	#ftrs.append('Average page rank old (soft)')
	ftrs.append('Std. dev. page rank old (soft)')
	#ftrs.append('Reciprocity (hard)')
	#ftrs.append('Reciprocity (soft)')
	ftrs.append('Average Jaccard similarity (hard)')
	ftrs.append('Std. dev. Jaccard similarity (hard)')
	ftrs.append('Average Jaccard similarity (soft)')
	ftrs.append('Std. dev. Jaccard similarity (soft)')
	ftrs.append('Number of edge betweenness communities (hard)')
	ftrs.append('Q of edge betweenness communities (hard)')
	ftrs.append('Average edge betweenness community size (hard)')
	ftrs.append('Std. dev. edge betweenness community size (hard)')
	ftrs.append('Number of fast-greedy communities (hard)')
	ftrs.append('Q of fast-greedy communities (hard)')
	ftrs.append('Average fast-greedy community size (hard)')
	ftrs.append('Std. dev. fast-greedy community size (hard)')
	ftrs.append('Number of fast-greedy communities (soft)')
	ftrs.append('Q of fast-greedy communities (soft)')
	ftrs.append('Average fast-greedy community size (soft)')
	ftrs.append('Std. dev. fast-greedy community size (soft)')
	ftrs.append('Number of walktrap communities (hard)')
	ftrs.append('Q of walktrap comminities (hard)')
	ftrs.append('Average walktrap community size (hard)')
	ftrs.append('Std. dev. walktrap community size (hard)')
	ftrs.append('Number of walktrap communities (soft)')
	ftrs.append('Q of walktrap comminities (soft)')
	ftrs.append('Average walktrap community size (soft)')
	ftrs.append('Std. dev. walktrap community size (soft)')
	for i in [2]:
		ftrs.append('3-motif %d (hard)'%(i+1))
	for i in [4, 6, 8]:
		ftrs.append('4-motif %d (hard)'%(i+1))
	for i in [2, 3]:
		ftrs.append('3-motif %d (soft)'%(i+1))
	for i in [4, 6, 7, 8, 9, 10]:
		ftrs.append('4-motif %d (soft)'%(i+1))
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

