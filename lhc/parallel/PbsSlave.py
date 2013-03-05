#!/usr/bin/python

import os
import tempfile
import shutil

from subprocess import Popen

def execute(cmd, lcldir, rmtdir, fname):
	# Write local then copy.
	prc_stdout = open(os.path.join(lcldir, fname), 'w')
	try:
		prc = Popen(cmd, stdout=prc_stdout)
	except OSError, e:
		prc_stdout.close()
		print cmd
		raise e
	prc.wait()
	prc_stdout.close()
	shutil.move(fname, os.path.join(rmtdir, fname)) # Includes rm

def main():
	# Change directory to the local /tmp.
	tmpdir = tempfile.mkdtemp()
	os.chdir(tmpdir)

	# Get the arguments from the environment.
	jobdir = os.environ['lc_jobdir']
	
	if os.environ['lc_superjob'] == '0':
		argkeys = sorted((key for key in os.environ if key.startswith('lc_arg')),
		 key=lambda x:int(x[6:]))
		argvals = [os.environ[key] for key in argkeys]
		execute(argvals, tmpdir, jobdir, os.environ['lc_filename'])
	else:
		infile = open(os.environ['lc_filename'])
		for line in infile:
			parts = line.split('\t')
			outfname = parts[0]
			cmd = parts[1:]
			execute(cmd, tmpdir, jobdir, outfname)
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
