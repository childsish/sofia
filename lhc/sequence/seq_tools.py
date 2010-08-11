#!/usr/bin/python

import numpy
import string

class Sequence:
	def __init__(self):
		pass

class DNASequence(Sequence):
	
	BASES = 'ACGT'
	
	def __init__(self):
		pass

class RNASequence(Sequence):
	
	BASES = 'ACGU'
	
	def __init__(self):
		pass

def gc(seq):
	gc = sum([seq.count(base) for base in 'gcGC'])
	return gc / float(len(seq))

NA2IDX = {'aa': 0, 'ac': 1, 'ag': 2, 'at': 3, 'au': 3,
 'ca': 4, 'cc': 5, 'cg': 6, 'ct': 7, 'cu': 7,
 'ga': 8, 'gc': 9, 'gg': 10, 'gt': 11, 'gu': 11,
 'ta': 12, 'tc': 13, 'tg': 14, 'tt': 15,
 'ua': 12, 'uc': 13, 'ug': 14, 'uu': 15}

def dinuc(seq, den=None):
	""" Returns an array of integers representing the dinucleotide content.
	 Base combinations follow the order:
	 aa ac ag at ca cc cg ct ga gc gg gt ta tc tg tt
	"""
	seq = seq.lower()
	res = numpy.zeros(16, dtype=numpy.float32)
	for i in xrange(len(seq) - 1):
		res[NA2IDX[seq[i:i + 2]]] += 1
	if den == None:
		den = len(seq)
	return res# / den

def rc(seq):
	m = string.maketrans('acgtuwrkysmbhdvnACGTUWRKYSMBHDVN', 'tgcaawymrskvdhbnTGCAAWYMRSKVDHBN')
	return seq.translate(m)[::-1]

if __name__ == '__main__':
	seq1 = 'atgattacggattcaagatctctggccgtcgttttacaacgtcgtgactgggaaaaccctggcgttacccaacttaatcgccttgcagcacatccccctttcgccagctggcgtaatagcgaagaggcccgcaccgatcgcccttcccaacagttgcgcagcctgaatggcgaatggtaa'
	seq2 = 'augauuacggauucaagaucccuggcaguuguuuuacaacgucgcgauugggaaaauccuggcgucacccaacuuaaccgccuugccgcacauccuccuuucgccagcuggcguaauagcgaggaagcccgcaccgaccgccccucucaacaguugcguagccugaauggcgaaugguaa'
	print dinuc(seq1)
	print dinuc(seq2)

"""
Complement transformation
a -> t
c -> g
g -> c
t -> a
u -> a
w -> w # Weak
r -> y # puRine
k -> m # Keto
y -> r # pYrimidine
s -> s # Strong
m -> k # M
b -> v # no a: B
h -> d # no g: H
d -> h # no c: D
v -> b # no tu: V
n -> n
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
M -> K # m
B -> V # NO A: b
H -> D # NO G: h
D -> H # NO C: d
V -> B # NO TU: v
N -> N
"""
