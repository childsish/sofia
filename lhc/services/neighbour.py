import paths
import os
import random
import subprocess
import sys
import tempfile

from numpy import empty, float32

class Neighbour:
	
	def __call__(self, mtx, tags):
		dirname = tempfile.mkdtemp()
		outfile = open(os.path.join(dirname, 'infile'), 'w')
		outfile.write(str(len(tags)).rjust(5) + '\n')
		for i in xrange(len(tags)):
			outfile.write(str(i).ljust(12) + ' '.join([str(round(val, 4)).ljust(6, '0') for val in mtx[i]]) + '\n')
		outfile.close()
		
		outfile = open(os.path.join(dirname, 'intree'), 'w')
		for i in xrange(50):
			seed = random.randint(0, sys.maxint)
			if seed%2 == 0:
				seed += 1
			prc = subprocess.Popen([paths.neighbour], stdin=subprocess.PIPE, stdout=subprocess.PIPE, cwd=dirname)
			print seed
			prc.communicate('J\n' + str(seed) + '\nY\n')
			infile = open(os.path.join(dirname, 'outtree'))
			outfile.write(infile.read())
			infile.close()
			os.remove(os.path.join(dirname, 'outfile'))
			os.remove(os.path.join(dirname, 'outtree'))
		outfile.close()
		
		prc = subprocess.Popen(['consense'], stdin=subprocess.PIPE, cwd=dirname)
		prc.communicate('Y\n')
		
		infile = open(os.path.join(dirname, 'outtree'))
		tree = ''.join(infile.read().split('\n'))
		infile.close()
		
		for i in xrange(len(tags)-1, -1, -1):
			tree = tree.replace(str(i) + ':', tags[i] + ':')
		
		outfile = open(os.path.join(dirname, 'treefile'), 'w')
		outfile.write(tree)
		outfile.close()
		
		print dirname
		return tree, dirname
	
	def createMatrix(self, data, measure):
		res = empty( (len(data), len(data)), dtype=float32 )
		
		for i in xrange(len(data)):
			for j in xrange(len(data)):
				if i == j:
					res[i, j] = 0.
				else:
					dst = measure(data[i], data[j])
					res[i, j] = dst
					res[j, i] = dst
		
		return res

neighbour = Neighbour()
