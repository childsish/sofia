#!/usr/bin/python

# Converted from the C. Burge and L. Katz C version to Python

import numpy
import random

class NonStandardException(Exception):
	def __init__(self):
		Exception.__init__(self)

class InvalidLengthException(Exception):
	def __init__(self, l):
		Exception.__init__(self)
		self.l = l

class CodonPair:
	def __init__(self):
		self.aa = None
		self.codon1 = None
		self.codon2 = None

class OrfData:
	def __init__(self):
		self.name = None
		self.start = None
		self.stop = None
		self.strand = None

def main(argv):
	orfnum = 0
	pos = 0
	extcodonflag = False
	codonfname = ''
	seedval = 0
	max_seq = 1
	
	orfs = [OrfData() for x in xrange(max_seq)]
	
	if len(argv) < 3 or len(argv) > 6:
		usage(argv[0])
	
	infname = argv[1]
	
	for i in xrange(3, len(argv)):
		if argv[i] == "-f":
			extcodonflag=True
			codonfname = argv[i+1]
		if argv[i] == "-r":
			seedval = int(argv[i+1])
	
	if seedval > 0:
		random.seed(seedval)
	
	infp = open(infname)
	
	sys.stderr.write("reading sequence ")
	
	seqs = readFasta(infname);
	acc, seq = seqs[0]
	
	sys.stderr.write(" seqlen %d bp\n"%len(seq));
	
	try:
		res = shuffle(seq,codonfname);
		print res
	except NonStandardException:
		sys.stderr.write("ERROR : Non-standard base found in file\n")
	except InvalidLengthException, e:
		sys.stderr.write("ERROR : len(seq) %d mod 3 = %d\n"%(e.l,e.l%3))

#/* fprintf(stderr,"\n\ndone\n\n"); */

#/****************************************************************************/

def usage(out_name):
	sys.stdout.write("\nusage: %s seqfile outfile [-r seedval] [-f codonfile]\n"%out_name)
	sys.stdout.write("\n       seqfile   : sequence file in (pseudo-)GenBank format\n")
	sys.stdout.write("\n       outfile   : file for final output\n");
	sys.stdout.write("\n       seedval   : value to use in seeding random number generator\n");
	sys.stdout.write("\n       codonfile : list of codon frequencies to use (optional)");
	sys.stdout.write("\n                   Format: XYZ f (64 lines)\n\n");
	sys.exit(0)


#/****************************************************************************/

def ribosome(a,b,c):
	if a in [0, 'A', 'a']:
		if b in [0, 'A', 'a']:
			if c in [0, 'A', 'a'] or c in [2, 'G', 'g']:
				return 8
			else:
				return 11
		if b in [1, 'C', 'c']:
			return 16
		if b in [2, 'G', 'g']:
			if c in [0, 'A', 'a'] or c in [2, 'G', 'g']:
				return 14
			else:
				return 15
		if b in [3, 'T', 't', 'U', 'u']:
			if c in [2, 'G', 'g']:
				return 10
			else:
				return 7
	
	if a in [1, 'C', 'c']:
		if b in [0, 'A', 'a']:
			if c in [0, 'A', 'a'] or c in [2, 'G', 'g']:
				return 13
			else:
				return 6
		if b in [1, 'C', 'c']:
			return 12
		if b in [2, 'G', 'g']:
			return 14
		if b in [3, 'T', 't', 'U', 'u']:
			return 9
	
	if a in [2, 'G', 'g']:
		if b in [0, 'A', 'a']:
			if c in [0, 'A', 'a'] or c in [2, 'G', 'g']:
				return 3
			else:
				return 2
		if b in [1, 'C', 'c']:
			return 0
		if b in [2, 'G', 'g']:
			return 5
		if b in [3, 'T', 't', 'U', 'u']:
			return 17
	
	if a in [3, 'T', 't', 'U', 'u']:
		if b in [0, 'A', 'a']:
			if c in [0, 'A', 'a'] or c in [2, 'G', 'g']:
				return 20
			else:
				return 19
		if b in [1, 'C', 'c']:
			return 15
		if b in [2, 'G', 'g']:
			if c in [0, 'A', 'a']:
				return 20
			if c in [2, 'G', 'g']:
				return 18
			if c in [1, 'C', 'c'] or c in [3, 'T', 't', 'U', 'u']:
				return 1
		if b in [3, 'T', 't', 'U', 'u']:
			if c in [0, 'A', 'a'] or c in [2, 'G', 'g']:
				return 9
			else:
				return 4
	return 21

def dcshuffle(seq, codonfname = ''):
	MAX_NUM_SEQ = 1
	
	aacodon = [None for x in xrange(22)]
	nextaacodon = [None for x in xrange(22)]
	swapflag = [None for x in xrange(22)]
	
	ntrueswap = 0
	
	shuffledaa = numpy.zeros(20, dtype=numpy.int32)
	
	tmpcodon = [None for x in xrange(4)]
	
	naa = numpy.zeros(22, dtype=numpy.int32)
	
	s = numpy.zeros(6, dtype=numpy.int32) # next 6 bases : int form
	c = [None for x in xrange(6)]

	mc = numpy.zeros((6, 4), dtype=numpy.int32) # base count in codon pos. 1-6
	md = numpy.zeros(6, dtype=numpy.float32) #demoninator for mc
	mf = numpy.zeros((6, 4), dtype=numpy.float32)
	mF = numpy.zeros((6, 4), dtype=numpy.float32)# mf multiplied by 100
	
	dic = numpy.zeros((3, 6, 4, 4), dtype=numpy.int32) # dicount at [p1,p2] of
	did = numpy.zeros((3, 6), dtype=numpy.float32)
	dif = numpy.zeros((3, 6, 4, 4), dtype=numpy.float32)
	
	tric = numpy.zeros((3, 4, 4, 4), dtype=numpy.int32) # tricount at 123,234,345
	trid = numpy.zeros(3, dtype=numpy.float32)
	trif = numpy.zeros((3, 4, 4, 4), dtype=numpy.float32)

	codonc = numpy.zeros((4, 4, 4), dtype=numpy.int32) # codon count
	codond = 0
	codonF = numpy.zeros((4, 4, 4), dtype=numpy.float32) # frequency multiplied by 100
	codstemF = numpy.zeros((4, 4), dtype=numpy.float32) # first two codon positons

	cumcodonF = numpy.zeros((4, 4, 4), dtype=numpy.float32)
	cumF = numpy.zeros((4, 4, 4), dtype=numpy.float32)

	hexc = numpy.zeros((4, 4, 4, 4, 4, 4), dtype=numpy.int32)
	hexd = 0.
	hexf = numpy.zeros((4, 4, 4, 4, 4, 4), dtype=numpy.float32)

	aac = numpy.zeros(22, dtype=numpy.int32) # 20 = stop, 21 = bogus letter
	aad = 0.
	aaf = numpy.zeros(22, dtype=numpy.float32)

	rho = numpy.zeros((3, 6, 4, 4), dtype=numpy.float32)# rho_ij at [p1,p2]

	nstdflag = 0;
	
	seq_num = numpy.array([nuc2num(base) for base in seq], dtype=numpy.int32)
		
	if len(seq)%3 != 0:
		raise InvalidLengthException(len(seq))
	
	for pos in xrange(0, len(seq_num) - 3, 3):
		
		s = seq_num[pos:pos+3]
		if pos + 6 <= len(seq_num):
			s = seq_num[pos:pos+6]
		
		aa = ribosome(s[0],s[1],s[2])
		aac[aa] += 1
		aad += 1
		
		if aa == 20:
			pass
		if aa == 21:
			nstdflag = 1
		
		if s[0] < 4 and s[1] < 4 and s[2] < 4:
			codonc[s[0],s[1],s[2]] += 1
			codond += 1
		
		for i in xrange(6):
			if s[i] < 4:
				mc[i,s[i]] += 1
				md[i] += 1
		
		for i in xrange(3):
			for j in xrange(i+1, 6):
				if s[i] < 4 and s[j] < 4:
					dic[i,j,s[i],s[j]] += 1
					did[i,j] += 1
		
		for i in xrange(3):
			if s[i] < 4 and s[i+1] < 4 and s[i+2] < 4:
				tric[i,s[i],s[i+1],s[i+2]] += 1
				trid[i] += 1
		
		if s[0] < 4 and s[1] < 4 and s[2] < 4 and s[3] < 4 and s[4] < 4 and s[5] < 4:
			hexc[s[0],s[1],s[2],s[3],s[4],s[5]] += 1
			hexd += 1
	
	if nstdflag:
		raise NonStandardException()
	
	for j in xrange(4):
		mf[:,j] = mc[:,j] / md
	mF = 100 * mf
	
	for i in xrange(3):
		for j in xrange(6):
			for k in xrange(4):
				for l in xrange(4):
					dif[i,j,k,l] = dic[i,j,k,l] / did[i,j]
					rho[i,j,k,l] = dif[i,j,k,l] / mf[i,k] * mf[j,l]
					if i == 0 and j == 1:
						codstemF[k,l] = 100 * dif[i,j,k,l]
	
	for i in xrange(3):
		for j in xrange(4):
			for k in xrange(4):
				for l in xrange(4):
					if i == 0:
						codonF[j,k,l] = 100 * codonc[j,k,l] / codond
					trif[i,j,k,l] = tric[i,j,k,l] / trid[i]
	
	hexf = hexc / hexd
	aaf = aac / aad
	
	res = []
		
	for i in xrange(22):
		if aac[i] > 0:
			aacodon[i] = aac[i] * ['']
			nextaacodon[i] = aac[i] * ['']
			swapflag[i] = aac[i] * ['']
		else:
			aacodon[i] = None
			nextaacodon[i] = None
	
	for j in xrange(0, len(seq)-3, 3):
		aa = ribosome(seq[j], seq[j+1], seq[j+2])
		#print type(aacodon[aa])
		#print type(int(naa[aa]))
		#print aacodon[aa][int(naa[aa])]
		#sys.exit(1)
		aacodon[aa][int(naa[aa])] = seq[j:j+3]
		nextaa = ribosome(seq[j+3], seq[j+4], seq[j+5])
		nextaacodon[aa][int(naa[aa])] = seq[j+3:j+6]
		naa[aa] += 1
	
	for i in xrange(20):
		shuffledaa[i] = i
	
	for j in xrange(20):
		r = 20 - j
		k = int(r*random.random())
		
		i = shuffledaa[j]
		shuffledaa[j] = shuffledaa[j+k]
		shuffledaa[j+k] = i
	
	# now shuffle the codons for each amino acid

	for h in xrange(20):# amino acid i
		i = int(shuffledaa[h])

		for j in xrange(aac[i]): # codon j
			r = aac[i]-j
			k = int(r*random.random())
			
			# consider swapping aacodon[i][j] with aacodon[i][j+k])
			
			# if codons are identical or if first nucleotides differ, do nothing
			
			if aacodon[i][j] == aacodon[i][j+k] or aacodon[i][j][0] != aacodon[i][j+k][0]:
				swapflag[i][j] = 1 # count as a swap */
			else: 
				
				# if +1 nucleotides are identical, make swap
				
				if nextaacodon[i][j][0] == nextaacodon[i][j+k][0]:
					aacodon[i][j], aacodon[i][j+k] = aacodon[i][j+k], aacodon[i][j]
					swapflag[i][j] = 1 # count as a swap
					ntrueswap += 1
				else:
					# define dinucleotide pair, identify reciprocal codon pairs
					# choose one at random, and make swap and reciprocal swap
					W = aacodon[i][j][2]
					X = nextaacodon[i][j][0]
					
					Y = aacodon[i][j+k][2]
					Z = nextaacodon[i][j+k][0]
					
					# if WX after YZ alphabetically, then swap WX, YZ dinucleotides
					
					if W > Y or (W == Y and X > Z):
						W, Y = Y, W
						X, Z = Z, X
						
					# Reciprocal dinucleotide pair: WZ, YX
					
					# Search through all remaining unswapped dicodons, identify reciprocal pairs
					
					nreciprocals = 0
					for ii in xrange(20): #aa ii\
						for jj in xrange(aac[ii]):
							if swapflag[ii][jj]: #exclude previously swapped codons
								pass
							else:
								for kk in xrange(jj+1, aac[ii]):
									if aacodon[ii][jj][0] != aacodon[ii][kk][0]: # exclude L2/L4, S2/S4 cases
										pass
									else:
										R = aacodon[ii][jj][2]
										S = nextaacodon[ii][jj][0]
										T = aacodon[ii][kk][2]
										U = nextaacodon[ii][kk][0]
										
										if (R == W and S == Z and T == Y and U == X) or\
											(T == W and U == Z and R == Y and S == X): # if reciprocal
											nreciprocals += 1
					
					reciprocals = None
					
					if nreciprocals > 0:
						reciprocals = [CodonPair() for x in xrange(nreciprocals)]
						
						recipnum = 0
						
						for ii in xrange(20): # aa ii
							for jj in xrange(aac[ii]):
								if swapflag[ii][jj]: #exclude previously swapped codons
									pass
								else: 
									for kk in xrange(jj+1, aac[ii]):
										if aacodon[ii][jj][0] != aacodon[ii][kk][0]:# exlude L2/L4, S2/S4 cases
											pass
										else:
											R = aacodon[ii][jj][2]
											S = nextaacodon[ii][jj][0]
											T = aacodon[ii][kk][2]
											U = nextaacodon[ii][kk][0]
											if (R == W and S == Z and T == Y and U == X) or\
												(T == W and U == Z and R == Y and S == X): # if reciprocal
												reciprocals[recipnum].aa = ii
												reciprocals[recipnum].codon1 = jj
												reciprocals[recipnum].codon2 = kk;
												recipnum += 1
						
						if nreciprocals > 0:
							recipnum = int(nreciprocals*random.random())
							
							ii = reciprocals[recipnum].aa
							jj = reciprocals[recipnum].codon1
							kk = reciprocals[recipnum].codon2
							
							# swap codons, swap reciprocal codons, update swapflags
							
							aacodon[i][j], aacodon[i][j+k] = aacodon[i][j+k], aacodon[i][j]
							
							swapflag[i][j] = 1 # count as a swap
							ntrueswap += 1
							
							aacodon[ii][jj], aacodon[ii][kk] = aacodon[ii][kk], aacodon[ii][jj]
							
							swapflag[ii][jj] = 1 # count as a swap
							ntrueswap += 1
	
	naa = numpy.zeros(22, dtype=numpy.int32)
	
	if codonfname:
		codonfp = open(codonfname)
		
		cumF=0.0
		
		cumcodonF = numpy.zeros((4, 4, 4), numpy.float32)
		
		for i in xrange(4):
			for j in xrange(4):
				for k in xrange(4):
					fscanf(codonfp,"%s %f",abc,f);
					codonF[i,j,k] = f
					cumF += f
					cumcodonF[i,j,k] = cumF
		
		codonfp.close()
	
	for j in xrange(0, len(seq) - 3, 3):
		aa = ribosome(seq[j],seq[j+1],seq[j+2])
		
		if len(codonfname) > 0:
			codonflag = 0
			
			while not codonflag:
				r = 100 * random.random()
				
				for i in xrange(4):
					for j in xrange(4):
						for k in xrange(4):
							if r < cumcodonF[i,j,k]:
								break
								
				aa2 = ribosome(nuc2num(i),nuc2num(j),nuc2num(k)); 
				
				if (aa2 == aa):
					codonflag = 1
				
				res.append("%c%c%c"%(nuc2num(i),nuc2num(j),nuc2num(k)))
		
		else:
			if aa == 20:
				res.append('tga')
			else:
				res.append("%s"%aacodon[aa][int(naa[aa])])
		
		if j%60 > 57:
			res.append('\n')
		
		naa[aa] += 1

	res.append(seq[-3:])
	
	return ''.join(res)

_alphabet = 'acgun'
alphabet = {'a': 0, 'c': 1, 'g': 2, 't': 3, 'u': 3, 'n': 4}
def nuc2num(nuc):
	if nuc in alphabet:
		return alphabet[nuc]
	return 4

aa_alphabet = 'ACDEFGHIKLMNPQRSTVWYxX'

def readFasta(filename):
	res = []
	
	infp = open(filename)
	lines = infp.readlines() # Faster to read in entire file
	infp.close()
	
	i = 0
	while i < len(lines):
		if lines[i][0] == '>':
			j = 1
			while i+j < len(lines) and lines[i+j][0] != '>':
				j += 1
			acc = lines[i].strip()[1:]
			seq = ''.join([line.strip() for line in lines[i+1:i+j]])
			res.append((acc, seq))
		i += j
	del lines # Only a precautionary measure
	
	return res

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
