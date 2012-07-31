#!/usr/bin/python

import numpy
import random

from sequence.seq_tools import dinuc

def convertFrequency(alp):
	din2idx = dict(('%s%s'%('acgu'[i/4], 'acgu'[i%4]), i) for i in xrange(16))
	num = numpy.zeros(16, dtype=numpy.int32)
	for k, v in alp.iteritems():
		num[din2idx[k]] = int(v)
	return num

def connectivity(frq):
	ncmp = 0 # Connectivity
	vis = numpy.zeros(len(frq), dtype=numpy.bool) # Visited nodes
	for i in xrange(len(frq)):
		if frq[i] == 0 or vis[i]:
			continue
		
		ncmp += 1
		stk = [i]
		vis[i] = True
		while len(stk) > 0: # Breadth first search.
			j = stk.pop(0)
			for k in xrange(4):
				up = k*4+j/4
				if not vis[up] and frq[up] > 0:
					stk.append(up)
					vis[up] = True
				dn = k+(j%4)*4
				if not vis[dn] and frq[dn] > 0:
					stk.append(dn)
					vis[dn] = True
	
	return ncmp

def imbalance(frq):
	res = numpy.zeros(4)
	for i in xrange(len(frq)):
		res[i/4] -= frq[i] # Consumed
		res[i%4] += frq[i] # Produced
	return res

def connected(frq, fr):
	res = numpy.zeros(len(frq))
	if frq[fr] == 0:
		raise Exception('Not a valid start point')
	res = numpy.zeros(len(frq))
	n = 0
	stk = [fr]
	while len(stk) > 0:
		top = stk.pop(0)
		res[top] = 1
		for j in xrange(top%4*4, top%4*4+4):
			if frq[j] > 0 and res[j] == 0:
				stk.append(j)
	
	return sum(res) == sum(frq > 0)

def generate(frq):
	res = []
	if connectivity(frq) > 1:
		return res
	
	# Calculate the imbalance
	imb = imbalance(frq)
	if sum(abs(imb)) == 1 or sum(abs(imb)) > 2:
		return res
	
	# Choose the next node
	if -1 in imb:
		fr = numpy.where(imb == -1)[0] * 4
		stk = [(i, frq, [i/4]) for i in xrange(fr, fr+4) if frq[i] > 0][::-1]
	else:
		stk = [(i, frq, [i/4]) for i in xrange(len(frq)) if frq[i] > 0][::-1]
	
	#random.shuffle(stk) # Start at a random dinucleotide (if more than one possible start).
	while len(stk) > 0:
		i, frq, pth = stk.pop()
		frq = frq.copy()
		pth = pth[:]
		
		# Adjust the frequencies and adjacency matrix
		frq[i] -= 1
		pth.append(i%4)
		if sum(frq) == 0:
			return ''.join(['acgu'[j] for j in pth])
			#res.append(''.join(['acgu'[j] for j in pth]))
			continue
		
		# Calculate the imbalance
		imb = imbalance(frq)
		
		# Choose the next node
		if connectivity(frq) > 1 or sum(abs(imb)) > 2:
			continue
		
		if -1 in imb:
			fr = numpy.where(imb == -1)[0] * 4
			nxt = [(j, frq, pth) for j in xrange(fr, fr+4) if frq[j] > 0]
		else:
			fr = (i%4)*4
			nxt = [(j, frq, pth) for j in xrange(fr, fr+4) if frq[j] > 0]
		
		#random.shuffle(nxt)
		stk.extend(nxt[::-1])
	return res

def main(argv):
	frq = {}
	for i in xrange(1, len(argv)):
		k, v = argv[i].split(':')
		frq[k] = int(v)
	frq = convertFrequency(frq)
	res = digen(frq)
	if res == None:
		print 'There are no possible sequences with this dinucleotide frequency'
	else:
		#for r in res:
		#	print r, dinuc(r)*len(r)
		print res
		print dinuc(res) * len(res)
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
