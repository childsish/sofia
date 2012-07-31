import os
import re
import subprocess
import tempfile

from paths import vienna

class RNAfold:
	
	OUT_PREFIX = '.out'
	DIR_PREFIX = '.dir'
	UBOX_REGX = re.compile('^(\d+) (\d+) (\d+\.\d+) ubox')
	
	def __call__(self, seqs, *args):
		handle, filename = tempfile.mkstemp()
		keys = sorted(seqs.keys())
		for i in xrange(len(keys)):
			os.write(handle, '>' + str(i) + '\n' + seqs[keys[i]] + '\n')
		os.close(handle)
		
		out_dir = filename + RNAfold.DIR_PREFIX
		os.mkdir(out_dir)
		prc_in = open(filename)
		prc_out = open(filename + RNAfold.OUT_PREFIX, 'w')
		prc = subprocess.Popen([vienna.rnafold] + list(args),
		                        stdin=prc_in,
		                        stdout=prc_out,
		                        cwd=out_dir)
		prc.wait()
		prc_out.close()
		prc_in.close()
		
		return filename
	
	def parseOutput(self, filename):
		if not filename.endswith(RNAfold.OUT_PREFIX):
			filename += RNAfold.OUT_PREFIX
		infile = open(filename)
		lines = infile.readlines()
		infile.close()
		
		step = 3
		if '>' not in lines[3]:
			step = 5
		
		stcs = len(lines)/step * [None]
		mfes = len(lines)/step * [None]
		for i in xrange(0, len(lines), step):
			parts = lines[i+2].split(' (')
			stcs[i/step] = parts[0]
			mfes[i/step] = float(parts[1][:-2])
		del lines
		
		return stcs, mfes
	
	def parseDotplot(self, filename):
		infile = open(filename)
		line = infile.readline()
		while line != '' and line != '%data starts here\n':
			line = infile.readline()
		line = infile.readline()
		
		res = []
		while line != '' and line != 'showpage\n':
			match = RNAfold.UBOX_REGX.search(line)
			if match:
				res.append((int(match.group(1)),
							int(match.group(2)),
							float(match.group(3))))
			line = infile.readline()
		infile.close()
		return res