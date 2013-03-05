import os
import re
import subprocess
import tempfile

from numpy import empty, float32
from paths.misc import meme

class Meme:
	
	POS_REGX = re.compile(r'	Motif \d+ sites sorted by position p-value')
	MTX_REGX = re.compile(r'	Motif \d+ position-specific probability matrix')
	MTX_PRP_REGX = re.compile(r'alength= ?(?P<len>\d+) w= ?(?P<wid>\d+)')
	
	def __call__(self, seqs, args=['-dna', '-nmotifs', '3', '-w', '8']):
		filename = None
		if isinstance(seqs, list):
			handle, filename = tempfile.mkstemp()
			for i in xrange(seqs):
				os.write(handle, '>' + str(i) + '\n' + seqs[i] + '\n')
			os.close(handle)
		elif isinstance(seqs, dict):
			handle, filename = tempfile.mkstemp()
			for key, val in seqs.iteritems():
				os.write(handle, '>' + key + '\n' + val + '\n')
			os.close(handle)
		elif isinstance(seqs, str):
			filename = os.path.abspath(seqs)
		else:
			raise TypeError('Needs list, dict or str')
		
		outfilehandle, outfilename = tempfile.mkstemp()
		prc = subprocess.Popen([meme, filename, '-text'] + list(args), stdout=outfilehandle)
		prc.wait()
		os.close(outfilehandle)
		
		return self.parse(outfilename), outfilename
		
	def parse(self, filename):
		infile = open(filename)
		lines = infile.readlines()
		infile.close()
		
		res = []
		poss = None
		mtx = None
		
		for i in xrange(len(lines)):
			if Meme.POS_REGX.match(lines[i]):
				poss = {}
				i += 4
				while ' ' in lines[i]:
					parts = lines[i].split()
					poss[parts[0]] = int(parts[1])
					i += 1
				
			if Meme.MTX_REGX.match(lines[i]):
				i += 2
				match = Meme.MTX_PRP_REGX.search(lines[i])
				if not match:
					raise Exception('Parse Error: unable to parse ' + lines[i]) #FIXME: Raise a proper exception
				mtx = empty( (int(match.group('wid')), int(match.group('len'))),
							dtype=float32)
				i += 1
				j = 0
				while ' ' in lines[i+j]:
					parts = lines[i+j].split()
					for k in xrange(len(parts)):
						mtx[j,k] = float(parts[k])
					j += 1
				res.append( (mtx, poss) )
		
		return res

