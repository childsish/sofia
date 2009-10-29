import os
import numpy
import tempfile

from seq_tools import gc
from paths.rna_tools import matrices
from paths.vienna import rnafold, rnaplfold
from subprocess import Popen, PIPE

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
		mfes = numpy.empty(len(seq), dtype=numpy.float32)
		for i in xrange(len(seq)):
			fr = i - win / 2
			if fr < 0:
				fr = 0
			to = i + win / 2
			if to > len(seq):
				to = len(seq)
			mfes[i] = self.mfe(seq[fr:to])
		return mfes
	
	def mfe(self, seq):
		self.__prc.stdin.write(seq + '\n')
		self.__prc.stdin.flush()
		self.__prc.stdout.readline()
		line = self.__prc.stdout.readline()
		if self.__p:
			self.__prc.stdout.readline()
			self.__prc.stdout.readline()
			self.__prc.stdout.readline()
		return float(line.split(' (')[1][:-2])
	
	def fold(self, seq):
		self.__prc.stdin.write(seq + '\n')
		self.__prc.stdin.flush()
		self.__prc.stdout.readline()
		line = self.__prc.stdout.readline()
		stc, mfe = line.split(' (')
		return stc, float(mfe[:-2])

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

def main(argv = None):
	if argv == None:
		argv = sys.argv
	
	seq = 'acgtgctagctagctagcgcggcatgctacgtagacgttagctagtcgtgggcgcgatctagatcgtagcagctagtcaatatattatctgatcgagctattataagcagctagcagcgatgcatcctgcgcgctagctgacg'
	tool = RNAFolder()
	print tool.scan(seq, 50)
	print tool.mfe(seq)

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
