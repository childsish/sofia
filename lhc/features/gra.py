#!/usr/bin/python

import igraph
import numpy
import os
import sys
import tempfile

from paths.rna import rnadistance
from paths.vienna import rnafold
from sequence.rna_tools import RNAFolder
from subprocess import Popen, PIPE
from ushuffle import shuffle
from FileFormats.FastaFile import iterFasta

CWD = tempfile.mkdtemp(dir='/home/childs/tmp')
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

def getGraPrps(seq):
	prps = []
	
	stc, mfe, emfe, cstc, cmfe, cdst, frq, div, bpp = FOLDER.fold(seq)
	
	 # Graph features
	adj = stc2adj(stc)
	for i in xrange(1, len(seq)):
		bpp[i-1,i] = 1
		bpp[i,i-1] = 1
	gra_h = igraph.Graph.Weighted_Adjacency(adj.tolist(), mode=igraph.ADJ_UPPER)
	gra_s = igraph.Graph.Weighted_Adjacency(bpp.tolist(), mode=igraph.ADJ_UPPER)
	
	prps.append(len(gra_h.articulation_points())) # Number of articulation points (hard)
	prps.append(len(gra_s.articulation_points())) # Number of articulation points (soft)
	
	prps.append(gra_h.average_path_length()) # Average shortest path length (hard)
	prps.append(gra_s.average_path_length()) # Average shortest path length (soft)
	
	a = gra_h.betweenness(directed=False)
	prps.append(numpy.mean(a)) # Average vertex betweenness (hard)
	 # Linear relation with path length (hard)
	prps.append(numpy.std(a)) # Std dev. vertex betweenness (hard)
	 # Linear relation with edge betweeness (hard)
	a = gra_s.betweenness(directed=False)
	prps.append(numpy.mean(a)) # Average vertex betweenness (soft)
	 # Linear relation with path length (soft)
	prps.append(numpy.std(a)) # Std dev. vertex betweenness (soft)
	 # Linear relation with edge betweeness (soft)

	a = gra_h.edge_betweenness(directed=False)
	prps.append(numpy.mean(a)) # Average edge betweenness (hard)
	prps.append(numpy.std(a))# Std dev. edge betweenness (hard)
	a = gra_s.edge_betweenness(directed=False)
	prps.append(numpy.mean(a)) # Average edge betweenness (soft)
	prps.append(numpy.std(a))# Std dev. edge betweenness (soft)
	
	prps.append(numpy.mean(gra_h.cocitation())) # Average cocitation distance (hard)
	 # Linear relation with graph density
	prps.append(numpy.mean(gra_s.cocitation())) # Average cocitation distance (soft)
	prps.append(numpy.mean(gra_h.bibcoupling())) # Average bibliographic coupling (hard)
	 # Linear relation with graph density
	prps.append(numpy.mean(gra_s.bibcoupling())) # Average bibliographic coupling (soft)
	
	a = gra_h.closeness()
	prps.append(numpy.mean(a)) # Average closeness centrality (hard)
	prps.append(numpy.std(a)) # Std. dev. closeness centrality (hard)
	a = gra_s.closeness()
	prps.append(numpy.mean(a)) # Average closeness centrality (soft)
	prps.append(numpy.std(a)) # Std. dev. closeness centrality (soft)
	
	a = gra_h.constraint(weights='weight')
	prps.append(numpy.mean(a)) # Average Burt's constraint (hard)
	 # Linear relation with graph density
	prps.append(numpy.std(a)) # Std. dev. Burt's constraint (hard)
	a = gra_s.constraint(weights='weight')
	prps.append(numpy.mean(a)) # Average Burt's constraint (soft)
	prps.append(numpy.std(a)) # Std. dev. Burt's constraint (soft)
	
	prps.append(numpy.mean(gra_h.degree())) # Average degree (hard)
	 # Linear relation with graph density
	prps.append(numpy.mean(gra_s.degree())) # Average degree (soft)
	 # Linear relation with graph density
	
	prps.append(gra_h.diameter(directed=False)) # Graph diameter (hard)
	prps.append(gra_s.diameter(directed=False)) # Graph diameter (soft)

	prps.append(gra_h.girth()) # Graph girth (hard)
	 # Always == 4
	prps.append(gra_s.girth()) # Graph girth (soft)
	 # Always == 3
	
	a = gra_h.coreness()
	prps.append(numpy.mean(a)) # Average coreness (hard)
	prps.append(numpy.std(a)) # Std. dev. coreness (hard)
	prps.append(numpy.max(a)) # Maximum coreness (hard)
	 # Always == 2
	a = gra_s.coreness()
	prps.append(numpy.mean(a)) # Average coreness (soft)
	prps.append(numpy.std(a)) # Std. dev. coreness (soft)
	prps.append(numpy.max(a)) # Maximum coreness (soft)
	
	prps.append(gra_h.density(True)) # Density (hard)
	prps.append(gra_s.density(True)) # Density (soft)

	prps.append(gra_h.transitivity_undirected()) # Transitivity (hard)
	 # Always == 0
	prps.append(gra_s.transitivity_undirected()) # Transitivity (soft)
	
	#a, b = gra_h.authority_score(return_eigenvalue=True)
	#prps.append(numpy.mean(a))
	#prps.append(numpy.std(a))
	#prps.append(b)
	a, b = gra_s.authority_score(return_eigenvalue=True)
	prps.append(numpy.mean(a))
	prps.append(numpy.std(a))
	prps.append(b)

	prps.append(gra_h.clique_number())
	prps.append(gra_s.clique_number())

	a = gra_h.count_multiple()
	prps.append(numpy.mean(a))
	prps.append(numpy.std(a))
	a = gra_s.count_multiple()
	prps.append(numpy.mean(a))
	prps.append(numpy.std(a))
	
	#a, b = gra_h.hub_score(return_eigenvalue=True)
	#prps.append(numpy.mean(a))
	#prps.append(numpy.std(a))
	#prps.append(b)
	a, b = gra_s.hub_score(return_eigenvalue=True)
	prps.append(numpy.mean(a))
	prps.append(numpy.std(a))
	prps.append(b)

	# Too computationally expensive
	#prps.append(gra_h.independence_number())
	#prps.append(gra_s.independence_number())

	prps.append(gra_h.mincut_value())
	prps.append(gra_s.mincut_value())
	
	a = gra_h.pagerank()
	prps.append(numpy.mean(a))
	prps.append(numpy.std(a))
	a = gra_s.pagerank()
	prps.append(numpy.mean(a))
	prps.append(numpy.std(a))

	a = gra_h.pagerank_old()
	prps.append(numpy.mean(a))
	prps.append(numpy.std(a))
	a = gra_s.pagerank_old()
	prps.append(numpy.mean(a))
	prps.append(numpy.std(a))
	
	prps.append(gra_h.reciprocity())
	prps.append(gra_s.reciprocity())

	a = gra_h.similarity_jaccard()
	prps.append(numpy.mean(a))
	prps.append(numpy.std(a))
	a = gra_s.similarity_jaccard()
	prps.append(numpy.mean(a))
	prps.append(numpy.std(a))
	
	a = gra_h.community_edge_betweenness(directed=False)
	prps.append(len(a))
	prps.append(a.q)
	prps.append(numpy.mean(a.sizes()))
	prps.append(numpy.std(a.sizes()))
	# Too computationally expensive
	#a = gra_s.community_edge_betweenness(directed=False)
	#prps.append(len(a))
	#prps.append(a.q)

	a = gra_h.community_fastgreedy(weights='weight')
	prps.append(len(a))
	prps.append(a.q)
	prps.append(numpy.mean(a.sizes()))
	prps.append(numpy.std(a.sizes()))
	a = gra_s.community_fastgreedy(weights='weight')
	prps.append(len(a))
	prps.append(a.q)
	prps.append(numpy.mean(a.sizes()))
	prps.append(numpy.std(a.sizes()))

	#a = gra_h.community_leading_eigenvector()
	#prps.append(len(a))
	#prps.append(a.q)
	#prps.append(numpy.mean(a.sizes()))
	#prps.append(numpy.std(a.sizes()))
	#a = gra_s.community_leading_eigenvector()
	#prps.append(len(a))
	#prps.append(a.q)
	#prps.append(numpy.mean(a.sizes()))
	#prps.append(numpy.std(a.sizes()))

	#a = gra_h.community_leading_eigenvector_naive()
	#prps.append(len(a))
	#prps.append(a.q)
	#prps.append(numpy.mean(a.sizes()))
	#prps.append(numpy.std(a.sizes()))
	#a = gra_s.community_leading_eigenvector_naive()
	#prps.append(len(a))
	#prps.append(a.q)
	#prps.append(numpy.mean(a.sizes()))
	#prps.append(numpy.std(a.sizes()))

	a = gra_h.community_walktrap(weights='weight')
	prps.append(len(a))
	prps.append(a.q)
	prps.append(numpy.mean(a.sizes()))
	prps.append(numpy.std(a.sizes()))
	a = gra_s.community_walktrap(weights='weight')
	prps.append(len(a))
	prps.append(a.q)
	prps.append(numpy.mean(a.sizes()))
	prps.append(numpy.std(a.sizes()))

	# Motifs of size 3 and 4. All have low F-scores
	a = gra_h.motifs_randesu(3)
	prps.append(a[0])
	prps.append(a[1])
	prps.append(a[2])
	prps.append(a[3])
	a = gra_h.motifs_randesu(4)
	prps.append(a[0])
	prps.append(a[1])
	prps.append(a[2])
	prps.append(a[3])
	prps.append(a[4])
	prps.append(a[5])
	prps.append(a[6])
	prps.append(a[7])
	prps.append(a[8])
	prps.append(a[9])
	prps.append(a[10])
	a = gra_s.motifs_randesu(3)
	prps.append(a[0])
	prps.append(a[1])
	prps.append(a[2])
	prps.append(a[3])
	a = gra_s.motifs_randesu(4)
	prps.append(a[0])
	prps.append(a[1])
	prps.append(a[2])
	prps.append(a[3])
	prps.append(a[4])
	prps.append(a[5])
	prps.append(a[6])
	prps.append(a[7])
	prps.append(a[8])
	prps.append(a[9])
	prps.append(a[10])
	
	return prps

def getRndFtrs(seq, n):
	prps = None
	for i in xrange(n):
		rseq = kshuffle(seq, 1)
		rprp = getGraPrps(rseq)
		if prps == None:
			prps = [[] for j in xrange(len(rprp))]
		for j in xrange(len(rprp)):
			prps[j].append(rprp[j])
	for i in xrange(len(prps)):
		prps[i] = numpy.mean(prps[i])
	return prps

def run(infname):
	for hdr, seq in iterFasta(infname):
		prps = getRndFtrs(seq, 1000)
		sys.stdout.write('\t'.join(map(str, prps)))
		sys.stdout.write('\n')
	
	# Cleanup
	for fname in os.listdir(CWD):
		os.remove(os.path.join(CWD, fname))
	os.rmdir(CWD)

def main(argv):
	infname = argv[1]
	run(infname)
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))

