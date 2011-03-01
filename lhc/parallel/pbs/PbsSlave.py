#!/usr/bin/python

import os
import tempfile
import shutil

from subprocess import Popen

def execute(cmd, lcldir, rmtdir, fname):
	# Write local then copy.
	prc_stdout = open(os.path.join(lcldir, fname))
	try:
		prc = Popen(cmd, stdout=prc_stdout)
	except OSError, e:
		prc_stdout.close()
		os.remove(prc_stdout)
		print cmd
		raise e
	prc.wait()
	prc_stdout.close()
	shutil.move(filename, os.path.join(rmtdir, fname)) # Includes rm

def main():
	# Change directory to the local /tmp.
	tmpdir = tempfile.mkdtemp()
	os.chdir(tmpdir)

	# Get the arguments from the environment.
	jobdir = os.environ['lc_jobdir']
	
<<<<<<< HEAD:parallel/pbs/PbsSlave.py
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
=======
	if os.environ['lc_superjob'] == '0':
		args = [val for key, val in sorted(os.environ.items(), key=lambda x:int(x[0][6:]))
		 if key.startswith('lc_arg')]
		execute(' '.join(args), tmpdir, jobdir, os.environ['lc_filename'])
	else:
		infile = open(os.environ['lc_filename'])
		for line in infile:
			outfname, cmd = line.split('\t')
			execute(cmd, tmpdir, jobdir, outfname)
		infile.close()
>>>>>>> 92a1ffad5ca9cf752ff091fe1d71e095ecc9b248:parallel/pbs/PbsSlave.py

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
