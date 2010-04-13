#!/usr/bin/python

import numpy
import os
import re
import tempfile

from seq_tools import gc
from paths.rna_tools import matrices
from paths.vienna import rnafold, rnaplfold, rnadistance, rnacofold
from subprocess import Popen, PIPE
from optparse import OptionParser

class RNACalibrator:
	def __init__(self):
		self.__mats = {}
		self.__lens = (numpy.arange(20) + 1) * 50
		self.__gcs = (numpy.arange(10) + 1) / 10.
		
		for filename in os.listdir(matrices):
			self.__mats[filename] = numpy.empty((len(self.__lens), len(self.__gcs)),
			 dtype=numpy.float32)
			infile = open(os.path.join(matrices, filename))
			for line in infile:
				x, y, z = line.split()
				self.__mats[filename][self.__closest(self.__lens, int(x)),
				 self.__closest(self.__gcs, float(y))] = float(z)
			infile.close()
	
	def calibrate(self, val, seq, prop):
		return val / self.__mats[prop][self.__closest(self.__lens, len(seq)),
		 self.__closest(self.__gcs, gc(seq))]
	
	def __closest(self, a, v):
		b = abs(v-a)
		return b.argsort()[0]

class RNAFolder:
	def __init__(self, p=False):
		self.__p = p
		self.cwd = tempfile.mkdtemp()
		args = [rnafold, '-noPS']
		if p: args.append('-p')
		self.__prc = Popen(args, stdin=PIPE, stdout=PIPE, close_fds=True, cwd=self.cwd)
	
	def __del__(self):
		for fname in os.listdir(self.cwd):
			os.remove(os.path.join(self.cwd, fname))
		os.rmdir(self.cwd)
		self.__prc.communicate()
	
	def scan(self, seq, win):
		stcs = []
		mfes = numpy.empty(len(seq), dtype=numpy.float32)
		for i in xrange(len(seq)):
			fr = i - win / 2
			if fr < 0:
				fr = 0
			to = i + win / 2
			if to > len(seq):
				to = len(seq)
			
			stc, mfe = self.fold(seq[fr:to])[:2]
			stcs.append(stc)
			mfes[i] = mfe
		return stcs, mfes

	def fold(self, seq):
		self.__prc.stdin.write(seq)
		self.__prc.stdin.write('\n')
		self.__prc.stdin.flush()
		
		# Sequence
		self.__prc.stdout.readline()
		
		# Minimum free energy structure and MFE
		line = self.__prc.stdout.readline()
		stc = line[:len(seq)]
		mfe = float(line[len(seq)+2:-2])
		
		if self.__p:
			# Ensemble structure and MFE
			line = self.__prc.stdout.readline()
			#estc = line[:len(seq)]
			emfe = float(line[len(seq)+2:-2])
			
			# Centroid structure and centroid MFE
			line = self.__prc.stdout.readline()
			cstc = line[:len(seq)]
			cmfe, cdst = line[len(seq)+2:-2].split()
			cmfe = float(cmfe)
			cdst = float(cdst[2:])

			# MFE frequency and ensemble diversity
			parts = self.__prc.stdout.readline().split()
			frq = float(parts[6][:-1])
			div = float(parts[9])
			
			# Base-pairing probabilities
			bpp = self.__readDot(os.path.join(self.cwd, 'dot.ps'))
			return stc, mfe, emfe, cstc, cmfe, cdst, frq, div, bpp
		return stc, mfe

	def __readDot(self, fname):
		res = None
		
		infile = open(fname)
		lines = infile.readlines()
		infile.close()
		for i in xrange(len(lines)):
			if lines[i].startswith('%'):
				continue
			elif lines[i].startswith('/sequence'):
				seq = []
				j = 1
				while '}' not in lines[i+j]:
					seq.append(lines[i+j].strip()[:-1])
					j += 1
				seq = ''.join(seq)
				res = numpy.zeros((len(seq), len(seq)), dtype=numpy.float32)
				for j in xrange(len(seq) - 1):
					res[j, j+1] = 1
					res[j+1, j] = 1
			elif lines[i][-5:-1] in ['ubox', 'lbox']:
				parts = lines[i].split()
				res[int(parts[0])-1, int(parts[1])-1] = 1 - float(parts[2]) # A higher probability = a shorter distance (ie. a smaller number)
		infile.close()
		
		return res

class RNADistance:
	def __init__(self, typ='-DP'):
		self.cwd = tempfile.mkdtemp()
		args = [rnadistance, typ]
		self.__prc = Popen(args, stdin=PIPE, stdout=PIPE, close_fds=True, cwd=self.cwd)
		self.__prc.stdin.write('\n') # Input no sequence
	
	def __del__(self):
		for fname in os.listdir(self.cwd):
			os.remove(os.path.join(self.cwd, fname))
		os.rmdir(self.cwd)
		self.__prc.communicate()

	def compareOneOne(self, seq1, seq2):
		self.__prc.stdin.write(seq1)
		self.__prc.stdin.write('\n')
		self.__prc.stdin.write(seq2)
		self.__prc.stdin.write('\n')
		self.__prc.stdin.flush()
		for line in self.__prc.stdout:
			print line
	
	#def compareOneMany(self, seq, seqs):
	#def compareAll(self, seqs):

class RNAHybrid:
	def __init__(self, p=False):
		self.__p = p
		self.cwd = tempfile.mkdtemp()
		args = [rnacofold, '-noPS']
		if p: args.append('-p')
		self.__prc = Popen(args, stdin=PIPE, stdout=PIPE, close_fds=True, cwd=self.cwd)
	
	def __del__(self):
		for fname in os.listdir(self.cwd):
			os.remove(os.path.join(self.cwd, fname))
		os.rmdir(self.cwd)
		self.__prc.communicate()

	def hybridise(self, seq1, seq2):
		seq = '%s&%s'%(seq1, seq2)
		self.__prc.stdin.write(seq)
		self.__prc.stdin.write('\n')
		self.__prc.stdin.flush()
		
		# Sequence
		self.__prc.stdout.readline()
		
		# Minimum free energy structure and MFE
		line = self.__prc.stdout.readline()
		stc = line[:len(seq)]
		mfe = float(line[len(seq)+2:-2])
		
		if self.__p:
			# Ensemble structure and MFE
			line = self.__prc.stdout.readline()
			#estc = line[:len(seq)]
			emfe = float(line[len(seq)+2:-2])
			
			# Centroid structure and centroid MFE
			line = self.__prc.stdout.readline()
			cstc = line[:len(seq)]
			cmfe, cdst = line[len(seq)+2:-2].split()
			cmfe = float(cmfe)
			cdst = float(cdst[2:])

			# MFE frequency and ensemble diversity
			parts = self.__prc.stdout.readline().split()
			frq = float(parts[6][:-1])
			div = float(parts[9])
			
			# Base-pairing probabilities
			bpp = self.__readDot(os.path.join(self.cwd, 'dot.ps'))
			return stc, mfe, emfe, cstc, cmfe, cdst, frq, div, bpp
		return stc, mfe

def calculateAccessibility(seq, w=50, u=4):
	cwd = tempfile.mkdtemp()
	prc = Popen([rnaplfold, '-W', '%d'%w, '-u', '%d'%u], stdin=PIPE, stdout=PIPE, cwd=cwd,
	 close_fds=True)
	prc.stdin.write(seq + '\n')
	prc.communicate()
	
	infile = open(os.path.join(cwd, 'plfold_lunp'))
	for i in xrange(u + 1):
		infile.readline()
	res = numpy.array([float(line.split()[-1]) for line in infile])
	infile.close()
	
	#infile = open(os.path.join(cwd, 'plfold_lunp'))
	#print infile.read()
	#infile.close()
	
	os.remove(os.path.join(cwd, 'plfold_dp.ps'))
	os.remove(os.path.join(cwd, 'plfold_lunp'))
	os.rmdir(cwd)
	
	return res

def scan(argv):
	from FileFormats.FastaFile import iterFasta
	
	parser = OptionParser()
	parser.set_defaults(prob=False, output=[], atgs=[], win=50)
	parser.add_option('-p', '--probability', action='store_true', dest='prob',
	 help='Calculate base pair probabiities')
	parser.add_option('-o', '--output', action='append', type='string', dest='output',
	 help='The types of output desired [stc, mfe].')
	parser.add_option('-0', '--atg', action='append', type='int', dest='atgs',
	 help='The start codon positions. If only one is provided, then it applies to all.')
	parser.add_option('-w', '--win', action='store', type='int', dest='win',
	 help='The size of the window.')
	parser.add_option('-r', '--range', action='store', type='int', nargs=2, dest='range',
	 help='Output only the given range.')
	options, args = parser.parse_args(argv[1:])
	
	infname = args[0]
	
	if 'mfe' in options.output:
		from rpy2.robjects import r
		from rpy2.robjects import numpy2ri
		r['pdf']('%s.scan.pdf'%infname[:infname.rfind('.')])
	
	folder = RNAFolder(options.prob)
	c_ent = 0
	for hdr, seq in iterFasta(infname):
		if len(options.atgs) == 0:
			atg = 0
		elif len(options.atgs) == 1:
			atg = options.atgs[0]
		else:
			atg = options.atgs[c_ent]
			
		stcs, mfes, dots = folder.scan(seq, options.win)
		if 'stc' in options.output:
			outfile = open('%s.scan.fasta'%(infname[:infname.rfind('.')]), 'w')
			for i in xrange(len(stcs)):
				outfile.write('>%s_%d\n%s\n'%(hdr, i, stcs[i]))
			outfile.close()
		if 'mfe' in options.output:
			f = 0
			t = len(mfes)
			if options.range:
				f = options.range[0]
				t = options.range[1]
			xs = numpy.arange(len(mfes)) - atg
			r['plot'](xs[f:t], mfes[f:t], ylab='Minimum Free Energy (kcal mol-1)',
			 xlab='Position', type='l', main=hdr)
		c_ent += 1
	
	if 'mfe' in options.output:
		r['dev.off']()

def main(argv):
	tool = RNADistance()
	tool.compareOneOne('((...(((...)))...))', '...(((...)))...')
	
	return 1
	if argv[1] == 'scan':
		scan(argv[1:])
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
