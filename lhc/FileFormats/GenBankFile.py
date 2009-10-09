#!/usr/bin/python

import re
import os

from GenBankFileUtility import Complement, Join, Range, tokenise, TokeniserError

RNG_REGX = re.compile(r'^<?(?P<fr>\d+)(?:\.\.>?(?P<to>\d+))?')

class GenBankFile:
	def __init__(self, filename):
		self.gc = '0'
		self.__filename = filename
		self.hdrs = {}
		self.ftrs = []
		self.rngs = []
		self.seq = ''
		
		infile = file(filename)
		lines = infile.readlines()
		infile.close()
		
		fr = 0
		while fr < len(lines):
			to = fr + 1
			while to < len(lines) and lines[to][0] == ' ':
				to += 1
			
			if lines[fr].startswith('FEATURES'):
				self.ftrs, self.rngs = self.__parseFtrs(lines, fr+1, to)
			elif lines[fr].startswith('ORIGIN'):
				self.seq = self.__parseSeq(lines, fr, to)
			elif lines[fr] == '//':
				break
			else:
				hdr, val = self.__parseHdr(lines, fr, to)
				self.hdrs.setdefault(hdr, []).append(val)
			
			fr = to
		del lines
		
		self.genes = self.__parseGenes(self.ftrs)
	
	def getGeneSeq(self, gene):
		return gene['range'].getSubSeq(self.seq)
	
	def linear_search(array, fr, x):
		_x = x
		if isinstance(x, tuple):
			_x = x[1]
		
		res = []
		while array[fr][0][0] < x[1]:
			fr += 1
	
	def binary_search(array, fr, to, x):
		if to - fr <= 1:
			self.linear_search(array, fr, x)
		
		_x = x
		if isinstance(x, tuple):
			_x = x[0]
		
		m = (fr + to) / 2
		if array[m][0][0] > _x:
			return self.binary_search(array, fr, m, x)
		return self.binary_search(array, m, to, x)
	
	def featureAt(self, x):
		idx = self.binary_search(self.rngs, 0, len(self.rngs), x)
		return self.ftrs[idx]
	
	def __parseHdrs(self, lines, fr, to, lvl):
		res = {}
		prv = fr
		for i in xrange(fr+1, to):
			if lines[i][lvl] != ' ':
				hdr, val = self.__parseHdr(lines, prv, i)
				if hdr == 'REFERENCE':
					res.setdefault(hdr, []).append(val)
				else:
					res[hdr] = val
				prv = i
		hdr, val = self.__parseHdr(lines, prv, to)
		res[hdr] = val
		return res
	
	def __parseHdr(self, lines, fr, to):
		hdr = lines[fr][:12].strip()
		
		if hdr == 'LOCUS':
			val = lines[fr][12:].split()
		elif hdr == 'SOURCE':
			i = fr + 1
			while lines[i][:12].strip() == '':
				i += 1
			src = ' '.join([lines[j][12:].strip() for j in xrange(fr, i)])
			org = lines[i][12:].strip()
			
			fr = i + 1
			i = fr + 1
			while i < to and lines[i][:12].strip() == '':
				i += 1
			lin = ' '.join([lines[j][12:].strip() for j in xrange(fr, i)])
			
			val = {hdr: src}
			val['ORGANISM'] = org
			val['LINEAGE'] = lin
		elif hdr == 'REFERENCE':
			val = self.__parseHdrs(lines, fr+1, to, 4)
			val[hdr] = lines[fr][12:].strip()
		else:
			val = []
			for i in xrange(fr, to):
				val.append(lines[i][12:].strip())
			val = ' '.join(val)
		return hdr, val
	
	def __parseFtrs(self, lines, fr, to):
		ftrs = []
		rngs = []
		
		prv = fr
		for i in xrange(fr+1, to):
			if lines[i][5] != ' ':
				try:
					ftr = self.__parseFtr(lines, prv, i)
					ftr['index'] = len(ftrs)
					ftrs.append(ftr)
					rngs.append(ftr['range'])
				except TokeniserError, e:
					print 'Unable to tokenise feature: %s\n Ignoring...'%lines[prv].strip()
				prv = i
		ftr = self.__parseFtr(lines, prv, to)
		ftr['index'] = len(ftrs)
		ftrs.append(ftr)
		rngs.append(ftr['range'])
		
		return ftrs, rngs
	
	def __parseFtr(self, lines, fr, to):
		res = {}
		
		# Parse the feature
		ftr = lines[fr][:21].strip()
		res['feature'] = ftr
		
		# Parse the range
		rng_str = lines[fr][21:].strip()
		i = fr + 1
		while i < to and lines[i][21] != '/':
			rng_str += lines[i].strip()
			i += 1
		rng = self.__parseSuperRange(tokenise(rng_str))
		res['range'] = rng
		
		
		while i < to:
			j = i + 1
			while j < to and lines[j][21] != '/':
				j += 1
			key, val = self.__parseQua(lines, i, j)
			res[key] = val
			i = j
		
		#if ftr == 'rRNA':
			#print res
			#print rng_str
			#print tokenise(rng_str)
		
		return res
	
	def __parseQua(self, lines, fr, to):
		key = None
		val = None
		
		line = lines[fr].strip()
		if not '=' in lines[fr]:
			key = line[1:]
			val = True
			return key, val
		
		key = line[1:line.find('=')]
		if key == 'translation':
			val = ''.join([line.strip() for line in lines[fr:to]])
		else:
			val = ' '.join([line.strip() for line in lines[fr:to]])
		
		val = val[val.find('=')+1:]
		val = val.replace('"', '')
		
		if key == 'codon_start':
			val = int(val) - 1
		
		return key, val
	
	def __parseGenes(self, ftrs):
		res = {}
		for i in xrange(len(ftrs)):
			ftr = ftrs[i]
			if ftr['feature'] in ['CDS', 'tRNA', 'rRNA']:
				if not 'gene' in ftr:
					if 'locus_tag' in ftr:
						ftr['gene'] = ftr['locus_tag']
					elif 'protein_id' in ftr:
						ftr['gene'] = ftr['protein_id']
					elif 'product' in ftr:
						ftr['gene'] = ftr['product']
					elif 'label' in ftr:
						ftr['gene'] = ftr['label']
					elif 'note' in ftr:
						ftr['gene'] = ftr['note']
					else:
						raise Exception('Unlabelled gene: %s'%str(ftr))
				res.setdefault(ftr['gene'], []).append(ftr)
		return res
	
	def __parseSeq(self, lines, fr, to):
		res = []
		for i in xrange(fr, to):
			res += lines[i][10:].split()
		res = ''.join(res)
		return res
	
	def __parseSuperRange(self, tokens):
		""" Parses a super range.
		 SuperRange ::= Range | Join | Complement
		"""
		if tokens[0].isdigit():
			return self.__parseRange(tokens)
		elif tokens[0] in ['join', 'order']:
			return self.__parseJoin(tokens)
		elif tokens[0] == 'complement':
			return self.__parseComplement(tokens)
		else:
			raise Exception('Range %s does not fit pattern.'%str(tokens))
	
	def __parseRange(self, tokens):
		""" Parses a range
		 Range ::= <num> | <num> ('..' | '^') <num>
		"""
		fr = int(tokens.pop(0)) - 1
		if len(tokens) > 1 and tokens[0] in ['..', '^']:
			tokens.pop(0) # Pop '..' | '^'
			to = int(tokens.pop(0))
			return Range(min(fr, to), max(fr, to))
		
		return Range(fr, fr + 1)
	
	def __parseJoin(self, tokens):
		""" Parses a join.
		 Join ::= 'join' '(' SuperRange [',' SuperRange] ')'
		"""
		res = []
		tokens.pop(0) # Pop 'join'
		tokens.pop(0) # Pop '('
		res.append(self.__parseSuperRange(tokens))
		while tokens[0] == ',':
			tokens.pop(0)
			res.append(self.__parseSuperRange(tokens))
		tokens.pop(0) # Pop ')'
		return Join(res)
	
	def __parseComplement(self, tokens):
		""" Parses a complement
		 Complement ::= 'complement' '(' SuperRange ')'
		"""
		tokens.pop(0) # Pop 'complement'
		tokens.pop(0) # Pop '('
		res = self.__parseSuperRange(tokens)
		tokens.pop(0) # Pop ')'
		return Complement(res)

def split(fname, outdir):
	infile = open(fname)
	files = infile.read().split('\n//\n')
	infile.close()
	
	for f in files:
		if f == '':
			continue
		
		outfname = '%s.txt'%f[:f.find('\n')].split()[1]
		outfile = open(os.path.join(outdir, outfname), 'w')
		outfile.write(f)
		outfile.write('\n//\n')
		outfile.close()

def main(argv = None):
	if argv == None:
		argv = sys.argv
	
	indir = argv[1]
	outdir = argv[2]
	for fname in os.listdir(indir):
		split(os.path.join(indir, fname), outdir)
	
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))