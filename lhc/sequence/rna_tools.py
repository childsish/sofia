#!/usr/bin/python

import os
import numpy
import tempfile

from seq_tools import gc
from paths.rna_tools import matrices
from paths.vienna import rnafold, rnaplfold
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
		args = [rnafold, '-noPS']
		if p: args.append('-p')
		self.__prc = Popen(args, stdin=PIPE, stdout=PIPE, close_fds=True)
	
	def __del__(self):
		self.__prc.communicate()
	
	def scan(self, seq, win):
		stcs = []
		mfes = numpy.empty(len(seq), dtype=numpy.float32)
		dots = []
		for i in xrange(len(seq)):
			fr = i - win / 2
			if fr < 0:
				fr = 0
			to = i + win / 2
			if to > len(seq):
				to = len(seq)
			stc, mfe, dot = self.fold(seq[fr:to])
			stcs.append(stc)
			mfes[i] = mfe
			dots.append(dot)
		return stcs, mfes, dots

	def fold(self, seq):
		self.__prc.stdin.write(seq + '\n')
		self.__prc.stdin.flush()
		self.__prc.stdout.readline()
		line = self.__prc.stdout.readline()
		dot = None
		if self.__p:
			self.__prc.stdout.readline()
			self.__prc.stdout.readline()
			self.__prc.stdout.readline()
			dot = self.__readDot('dot.ps')
		stc, mfe = line.split(' (')
		return stc, float(mfe[:-2]), dot

	def __readDot(self, fname):
		res = None
	
		record = False
		infile = open(fname)
		lines = infile.readlines()
		infile.close()
		for i in xrange(len(lines)):
			if lines[i].startswith('/sequence'):
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
			elif lines[i] == '%data starts here\n':
				record = True
			elif lines[i] == 'showpage\n':
				record = False
			elif record:
				parts = lines[i].split()
				res[int(parts[0])-1, int(parts[1])-1] = 1 - float(parts[2]) # A higher probability = a shorter distance (ie. a smaller number)
		infile.close()
	
		return res	

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
	if argv[1] == 'fold':
		print 'Use RNAfold you twit!'
	elif argv[1] == 'scan':
		scan(argv[1:])

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
