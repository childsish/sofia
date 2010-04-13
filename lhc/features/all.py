#!/usr/bin/python

import igraph
import numpy
import os
import sys
import tempfile
import time

from paths.rna import rnadistance
from paths.vienna import rnafold
from sequence.rna_tools import RNAFolder
from subprocess import Popen, PIPE
from ushuffle import shuffle
from FileFormats.FastaFile import readFasta

CWD = tempfile.mkdtemp(dir='/home/childs/tmp')
ENSEMBLE_SIZE = 1000
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

	#t = time.time()
	#tt = t
	
	stc, mfe, emfe, cstc, cmfe, cdst, frq, div, bpp = FOLDER.fold(seq)
	
	 # RNAfold features
	prps.append(mfe) # Minimum free energy
	prps.append(emfe) # Ensemble MFE
	prps.append(cmfe) # Centroid MFE
	prps.append(cdst) # Centroid distance
	 # F < 0.05
	prps.append(frq) # MFE structure frequency in ensemble
	 # F < 0.05
	prps.append(div) # Ensemble diversity
	 # F < 0.05
	prps.append(entropy(bpp)) # Shannon entropy of base-pairing probabilities

	
	#print 'RNAfold features', time.time() - t
	#t = time.time()

	 # Structural features
	a, b, c, d, e, f = structuralFeatures(stc)
	 # Hairpin loops - number, total size, average size # F < 0.05
	if len(a) == 0:
		prps.extend((0, 0, 0))
	else:
		prps.append(len(a)) # Keep (Unshuffled = 0.04)
		prps.append(numpy.sum(a))
		prps.append(numpy.mean(a))
	 # Multi-loops - number, total size, average size # F < 0.05
		prps.append(len(b))
	if len(b) == 0:
		prps.extend((0, 0))
	else:
		prps.append(numpy.sum(b))
		prps.append(numpy.mean(b))
	 # Internal loops - number, total size, average size, average imbalance
	if len(c) == 0:
		prps.extend((0, 0, 0, 0))
	else:
		prps.append(len(c))
		prps.append(numpy.sum([sum(c_) for c_ in c]))
		prps.append(numpy.mean([sum(c_) for c_ in c]))
		prps.append(numpy.mean([abs(c_[0] - c_[1]) for c_ in c]))
	 # Bulges - number, total size, average size
	if len(d) == 0:
		prps.extend((0, 0, 0))
	else:
		prps.append(len(d))
		prps.append(numpy.sum(d))
		prps.append(numpy.mean(d))
	 # Stems - number, total size, average size
	if len(e) == 0:
		prps.extend((0, 0, 0))
	else:
		prps.append(len(e)) # Keep (Shuffled = 0.04)
		prps.append(numpy.sum(e))
		prps.append(numpy.mean(e)) # Keep (Shuffled = 0.07)
	 # Branches - number, total size, average size
	if len(f) == 0:
		prps.extend((0, 0, 0))
	else:
		prps.append(len(f))
		prps.append(numpy.sum(f))
		prps.append(numpy.mean(f))
	
	#print 'Structural features', time.time() - t
	#t = time.time()

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
	 # F < 0.05actgtgctagtcgatcgggcgtacgtagtagtcgtagtgctg
	prps.append(bss) # Between cluster sum of squares (Ding centroid)
	 # F < 0.05
	prps.append(numpy.mean(wss)) # Average within cluster sum of squares (Ding centroid)
	 # F < 0.05
	prps.append(bss2) # Between cluster sum of squares (distance centroid)
	 # F < 0.05
	prps.append(numpy.mean(wss2)) # Average within cluster sum of squares (distance centroid)
	 # F < 0.05

	#print 'Ensemble features', time.time() - t
	#t = time.time()

	 # Graph features
	adj = stc2adj(stc)
	gra_h = igraph.Graph.Weighted_Adjacency(adj.tolist(), mode=igraph.ADJ_UPPER)
	gra_s = igraph.Graph.Weighted_Adjacency(bpp.tolist(), mode=igraph.ADJ_UPPER)

	prps.append(len(gra_h.articulation_points())) # Number of articulation points (hard)
	prps.append(len(gra_s.articulation_points())) # Number of articulation points (soft)

	#print 'Articulation points', time.time() - t
	
	prps.append(gra_h.average_path_length()) # Average shortest path length (hard)
	prps.append(gra_s.average_path_length()) # Average shortest path length (soft)
	
	#print 'Average shortest path length', time.time() - t
	
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
	
	#print 'Betweenness', time.time() - t

	prps.append(numpy.mean(gra_h.cocitation())) # Average cocitation distance (hard)
	 # Linear relation with graph density
	prps.append(numpy.mean(gra_s.cocitation())) # Average cocitation distance (soft)
	prps.append(numpy.mean(gra_h.bibcoupling())) # Average bibliographic coupling (hard)
	 # Linear relation with graph density
	prps.append(numpy.mean(gra_s.bibcoupling())) # Average bibliographic coupling (soft)

	#print 'Cocitation/bibcoupling', time.time() - t
	
	a = gra_h.closeness()
	prps.append(numpy.mean(a)) # Average closeness centrality (hard)
	prps.append(numpy.std(a)) # Std. dev. closeness centrality (hard)
	a = gra_s.closeness()
	prps.append(numpy.mean(a)) # Average closeness centrality (soft)
	prps.append(numpy.std(a)) # Std. dev. closeness centrality (soft)

	#print 'Closeness', time.time() - t
	
	a = gra_h.constraint(weights='weight')
	prps.append(numpy.mean(a)) # Average Burt's constraint (hard)
	 # Linear relation with graph density
	prps.append(numpy.std(a)) # Std. dev. Burt's constraint (hard)
	a = gra_s.constraint(weights='weight')
	prps.append(numpy.mean(a)) # Average Burt's constraint (soft)
	prps.append(numpy.std(a)) # Std. dev. Burt's constraint (soft)

	#print 'Constraint', time.time() - t
	
	prps.append(numpy.mean(gra_h.degree())) # Average degree (hard)
	 # Linear relation with graph density
	prps.append(numpy.mean(gra_s.degree())) # Average degree (soft)
	 # Linear relation with graph density

	#print 'Degree', time.time() - t
	
	prps.append(gra_h.diameter(directed=False)) # Graph diameter (hard)
	prps.append(gra_s.diameter(directed=False)) # Graph diameter (soft)

	#print 'Diameter', time.time() - t

	prps.append(gra_h.girth()) # Graph girth (hard)
	 # Always == 4
	prps.append(gra_s.girth()) # Graph girth (soft)
	 # Always == 3

	#print 'Girth', time.time() - t
	
	a = gra_h.coreness()
	prps.append(numpy.mean(a)) # Average coreness (hard)
	prps.append(numpy.std(a)) # Std. dev. coreness (hard)
	prps.append(numpy.max(a)) # Maximum coreness (hard)
	 # Always == 2
	a = gra_s.coreness()
	prps.append(numpy.mean(a)) # Average coreness (soft)
	prps.append(numpy.std(a)) # Std. dev. coreness (soft)
	prps.append(numpy.max(a)) # Maximum coreness (soft)

	#print 'Coreness', time.time() - t
	
	prps.append(gra_h.density(True)) # Density (hard)
	prps.append(gra_s.density(True)) # Density (soft)

	#print 'Density', time.time() - t

	prps.append(gra_h.transitivity_undirected()) # Transitivity (hard)
	 # Always == 0
	prps.append(gra_s.transitivity_undirected()) # Transitivity (soft)

	#print 'Transitivity', time.time() - t

	#print 'Graph features (original)', time.time() - t
	#t = time.time()

	#a, b = gra_h.authority_score(return_eigenvalue=True)
	#prps.append(numpy.mean(a))
	#prps.append(numpy.std(a))
	#prps.append(b)
	a, b = gra_s.authority_score(return_eigenvalue=True)
	prps.append(numpy.mean(a))
	prps.append(numpy.std(a))
	prps.append(b)

	#print 'Authority', time.time() - t

	prps.append(gra_h.clique_number())
	prps.append(gra_s.clique_number())

	#print 'Clique', time.time() - t

	a = gra_h.count_multiple()
	prps.append(numpy.mean(a))
	prps.append(numpy.std(a))
	a = gra_s.count_multiple()
	prps.append(numpy.mean(a))
	prps.append(numpy.std(a))

	#print 'Count multiple', time.time() - t
	
	#a, b = gra_h.hub_score(return_eigenvalue=True)
	#prps.append(numpy.mean(a))
	#prps.append(numpy.std(a))
	#prps.append(b)
	a, b = gra_s.hub_score(return_eigenvalue=True)
	prps.append(numpy.mean(a))
	prps.append(numpy.std(a))
	prps.append(b)

	#print 'Hub score', time.time() - t

	# Too computationally expensive
	#prps.append(gra_h.independence_number())
	#prps.append(gra_s.independence_number())
	#print 'Independence number', time.time() - t

	prps.append(gra_h.mincut_value())
	prps.append(gra_s.mincut_value())

	#print 'Mincut', time.time() - t
	
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

	#print 'Pagerank', time.time() - t
	
	prps.append(gra_h.reciprocity())
	prps.append(gra_s.reciprocity())

	#print 'Reciprocity', time.time() - t

	a = gra_h.similarity_jaccard()
	prps.append(numpy.mean(a))
	prps.append(numpy.std(a))
	a = gra_s.similarity_jaccard()
	prps.append(numpy.mean(a))
	prps.append(numpy.std(a))

	#print 'Jaccard similarity', time.time() - t

	#print 'Graph features (new)', time.time() - t
	#t = time.time()
	
	a = gra_h.community_edge_betweenness(directed=False)
	prps.append(len(a))
	prps.append(a.q)
	prps.append(numpy.mean(a.sizes()))
	prps.append(numpy.std(a.sizes()))
	# Too computationally expensive
	#a = gra_s.community_edge_betweenness(directed=False)
	#prps.append(len(a))
	#prps.append(a.q)

	#print 'Community edge betweeness', time.time() - t

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

	#print 'Community fastgreedy', time.time() - t

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
	#print 'Community leading eigenvector', time.time() - t

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
	#print 'Community leading eigenvector naive', time.time() - t

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

	#print 'Community walktrap', time.time() - t

	#print 'Graph features (clustering/community)', time.time() - t
	##t = time.time()
	
	# Long calculation times and not predictive.
	#  Perhaps use RNAplfold
	#a = scanStability(seq)
	#if len(a) == 0:
	#	a = [0]
	#prps.append(numpy.mean(a))
	#prps.append(numpy.std(a))
	#prps.append(numpy.max(a))
	#a = growStability(seq[:100])
	#if len(a) == 0:
	#	a = [0]
	#prps.append(numpy.mean(a))
	#prps.append(numpy.std(a))
	#prps.append(numpy.max(a))

	# Motifs of size 3 and 4. All have low F-scores
	#a = gra_h.motifs_randesu(3)
	#prps.append(a[0])
	#prps.append(a[1])
	#prps.append(a[2])
	#prps.append(a[3])
	#a = gra_h.motifs_randesu(4)
	#prps.append(a[0])
	#prps.append(a[1])
	#prps.append(a[2])
	#prps.append(a[3])
	#prps.append(a[4])
	#prps.append(a[5])
	#prps.append(a[6])
	#prps.append(a[7])
	#prps.append(a[8])
	#prps.append(a[9])
	#prps.append(a[10])
	#a = gra_s.motifs_randesu(3)
	#prps.append(a[0])
	#prps.append(a[1])
	#prps.append(a[2])
	#prps.append(a[3])
	#a = gra_s.motifs_randesu(4)
	#prps.append(a[0])
	#prps.append(a[1])
	#prps.append(a[2])
	#prps.append(a[3])
	#prps.append(a[4])
	#prps.append(a[5])
	#prps.append(a[6])
	#prps.append(a[7])
	#prps.append(a[8])
	#prps.append(a[9])
	#prps.append(a[10])
	#print 'Graph features (motifs)', time.time() - t
	
	#print 'Total time', time.time() - tt

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

def scanStability(seq):
	win = 67 # FIXME: Magic number
	stc, mfe, bpp = FOLDER.fold(seq[win:win*2])
	pairs = getPairs(stc)
	res = dict([((pair[0]+win, pair[1]+win), 0) for pair in pairs])
	for i in xrange(len(seq) - win): 
		stc, mfe, bpp = FOLDER.fold(seq[i:i+win])
		for pair in getPairs(stc):
			adj_pair = (pair[0] + i, pair[1] + i)
			if adj_pair in res:
				res[adj_pair] += 1
	return res.values()

def growStability(seq):
	res = {}
	for i in xrange(len(seq)-1):
		stc, mfe, bpp = FOLDER.fold(seq[:i+1])
		for pair in getPairs(stc):
			res.setdefault(pair, 0)
			res[pair] += 1
	return res.values()

def entropy(bpp):
	ttl = numpy.empty(bpp.shape[0])
	for i in xrange(bpp.shape[0]):
		ttl[i] = -sum([bpp[i,j] * numpy.log(bpp[i,j]) for j in xrange(i, bpp.shape[1])
		 if bpp[i,j] != 0])
	return numpy.mean([t for t in ttl if t != 0])

def structuralFeatures(stc):
	hloops = []
	mloops = []
	iloops = []
	bulges = []
	stems = []
	branches = []
	
	lvls = [[]]
	c_lvl = 0
	c_stem = 0
	for i in xrange(len(stc)):
		
		if stc[i] == '(':
			lvls[c_lvl].append('(')
			lvls.append([])
			c_lvl += 1
		elif stc[i] == ')':
			p_lvl = lvls.pop()
			c_lvl -= 1
			
			if p_lvl.count('(') == 0:
				hloops.append(len(p_lvl))
			elif p_lvl.count('(') == 1 and p_lvl.count('.') > 0:
				if p_lvl[0] == '.' and p_lvl[-1] == '.':
					iloops.append((p_lvl.index('('), len(p_lvl) - p_lvl.index('(') - 1))
				else:
					bulges.append(len(p_lvl)-1)
			elif '.' in p_lvl:
				mloops.append(len(p_lvl) - p_lvl.count('('))
				branches.append(p_lvl.count('('))
			
			if p_lvl != ['('] and c_stem != 0:
				stems.append(c_stem)
				c_stem = 0
			c_stem += 1
		elif stc[i] == '.':
			if c_lvl == 0:
				continue
			lvls[c_lvl].append('.')
	stems.append(c_stem)

	return hloops, mloops, iloops, bulges, stems, branches

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
	 close_fds=True, cwd=CWD, stdout=PIPE)
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
	prc = Popen([rnadistance, '-DP', '-Xm'], stdin=prc_stdin, stdout=PIPE, close_fds=True)
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
	prc = Popen([rnadistance, '-DP', '-Xf'], stdin=PIPE, stdout=PIPE, close_fds=True)
	prc.stdin.write(seq)
	prc.stdin.write('\n')
	prc.stdin.write(stc)
	prc.stdin.write('\n')
	prc.stdin.write('\n'.join(stcs))
	prc.stdin.write('\n')
	lines = prc.communicate()[0].split('\n')
	res = numpy.array([int(line.split()[1]) for line in lines if line != ''])
	return res

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
	ents = readFasta(infname)

	for hdr, seq in ents:
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

