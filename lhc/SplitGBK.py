#!/usr/bin/python

import os
import sys

filenames = [filename for filename in os.listdir(sys.argv[1]) if filename.endswith('.gb')]
for filename in filenames:
	infile = open(os.path.join(sys.argv[1], filename))
	line = infile.readline()

	outfile = open(os.path.join(sys.argv[1], line.split()[1] + '.gbk'), 'w')
	outfile.write(line)
	for line in infile:
		if line.startswith('LOCUS'):
			outfile.close()
			outfile = open(os.path.join(sys.argv[1], line.split()[1] + '.gbk'), 'w')
		outfile.write(line)
	outfile.close()
