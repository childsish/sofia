#!/usr/bin/python

import os
import subprocess

from paths import librfam, cmsearch

CMDIR = 'cm'

def classifySeqs(filename):
	cmfiles = sorted(os.listdir(os.path.join(librfam, CMDIR)))
	
	res = {}
	
	for i in xrange(len(cmfiles)):
		#print cmfiles[i]
		prc = subprocess.Popen([cmsearch, os.path.join(librfam, CMDIR, cmfiles[i]), filename], stdout=subprocess.PIPE)
		for line in prc.stdout:
			if line[0] == '>':
				acc = line[1:-1]
			if line.startswith(' Score = '):
				score = float(line[9:line.find(',')])
				#print score
				try:
					if score > res[acc][1]:
						res[acc] = (cmfiles[i][:-3], score)
				except KeyError, e:
					res[acc] = (cmfiles[i][:-3], score)
	return res

def main(argv = None):
	if argv == None:
		argv = sys.argv
	
	res = classifySeqs(argv[1])
	
	infile = open(argv[1])
	lines = infile.readlines()
	infile.close()
	accs = [lines[i][1:-1] for i in xrange(0, len(lines), 2)]
	del lines
	
	outfile = open(argv[2], 'w')
	for acc in accs:
		outfile.write(acc + '\t' + res[acc][0] + '\t' + str(round(res[acc][1], 3)) + '\n')
	outfile.close()
	
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))
