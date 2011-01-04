#!/usr/bin/python

import numpy
import string

def gc(seq):
	gc = sum([seq.count(base) for base in 'gcGC'])
	return gc / float(len(seq))
	
def getKmers(k):
	kmers = set()
	bases = 'acgt'
	stk = [[j] for j in bases]
	while len(stk) > 0:
		seq = stk.pop()
		if len(seq) == k:
			kmers.add(''.join(seq))
		else:
			for j in bases:
				cpy = seq[:]
				cpy.append(j)
				stk.append(cpy)
	return kmers

def kContent(seq, k):
	kmers = getKmers(k)
	res = dict([(kmer, 0.) for kmer in kmers])
	for i in xrange(len(seq) - k + 1):
		res[seq[i:i + k]] += 1
	return res

"""
Complement transformation (Degenerate Code)
a -> t
c -> g
g -> c
t -> a
u -> a
w -> w # Weak   	(AU)
r -> y # puRine 	(AG)
k -> m # Ketone 	(GU)
y -> r # pYrimidine	(CU)
s -> s # Strong 	(CG)
m -> k # aMino  	(AC)
b -> v # no a: B	(CGU)
h -> d # no g: H	(ACU)
d -> h # no c: D	(AGU)
v -> b # no tu: V	(ACG)
n -> n # aNy    	(ACGU)
A -> T
C -> G
G -> C
T -> A
U -> A
W -> W # wEAK
R -> Y # PUrINE
K -> M # kETO
Y -> R # PyRIMIDINE
S -> S # sTRONG
M -> K # AmINO
B -> V # NO A: b
H -> D # NO G: h
D -> H # NO C: d
V -> B # NO TU: v
N -> N # AnY
"""
