#!/usr/bin/python

import os
import tempfile
import shutil

from paths.multiple_sequences import clustalw2
from subprocess import Popen

REPLACEME = '@@'

def main():
	# Change directory to the local /tmp.
	tmpdir = tempfile.mkdtemp()
	os.chdir(tmpdir)

	# Get the arguments from the environment.
	jobdir = os.environ['lc_jobdir']
	taskid = int(os.environ['lc_taskid'])
	filename = os.environ['lc_filename']
	args = [i for i in os.environ.items() if i[0].startswith('lc_arg')]
	args.sort(key=lambda x:int(x[0][6:]))
	args = [arg[1] for arg in args]
	
	# Each line in the file is a job to run.
	infile = open(filename)
	for line in infile:
		c_filename = line.strip()
		c_args = args[:]
		for i in xrange(len(c_args)):
			if REPLACEME in c_args[i]:
				c_args[i] = c_args[i].replace(REPLACEME, c_filename)
	
		# Write local then copy.
		handle, filename = tempfile.mkstemp()
		prc_stdout = os.fdopen(handle, 'w')
		try:
			prc = Popen(c_args, stdout=prc_stdout)
		except OSError, e:
			prc_stdout.close()
			os.remove(filename)
			print c_args
			raise e
		prc.wait()
		prc_stdout.close()
		o_filename = os.path.basename(c_filename)
		shutil.move(filename, os.path.join(jobdir, o_filename)) # Includes rm
	infile.close()

	for root, dirs, files in os.walk(tmpdir, topdown=False):
		for name in files:
			os.remove(os.path.join(root, name))
		for name in dirs:
			os.rmdir(os.path.join(root, name))
	os.rmdir(tmpdir)
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main())

