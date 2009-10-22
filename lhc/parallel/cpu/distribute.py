#!/usr/bin/python

""" distribute.py
A class designed to distribute jobs on the cluster. Options are available to
limit the maximum number of nodes used and, in the case of large numbers of
small jobs, group jobs together into a smaller number of "super jobs". The time
in between checking if a job is complete can also be altered.

TODO:
1. Path extensions. ~/path works because the os expands it before running the
program. ../path does not work.

2. Change the code to allow the appending of jobs as they are created instead
of setting everything up at the start and submitting all in one go. This would
provide greater flexibility with no extra cost.

3. Redirection (pipes) doesn't work.
"""

import os
import sys
import tempfile
import time

from optparse import OptionParser
from paths import cluster
from subprocess import Popen, PIPE

USAGE = """usage: %prog [options] executable [executable_args]"""

class ClusterJob:
	def __init__(self, label, args, taskid, logdir):
		self.label = label
		self.args = args
		self.taskid = taskid
		self.jobid = None
		self.logdir = logdir

	def __del__(self):
		if self.jobid != None and self.isAlive():
			prc = Popen([cluster.qdel, self.jobid], stdout=PIPE, stderr=PIPE)
			stdout, stderr = prc.communicate()
			sys.stdout.write(stdout)
			sys.stderr.write(stderr)
	
	def start(self):
		prc = Popen(self.args, stdout=PIPE, stderr=PIPE)
		stdout, stderr = prc.communicate()
		if stderr != '':
			raise Exception(stderr)
		self.jobid = stdout.strip()
	
	def isAlive(self):
		if self.jobid == None:
			return False
		prc = Popen([cluster.qstat, self.jobid], stdout=PIPE, stderr=PIPE)
		stdout, stderr = prc.communicate()
		
		return stderr.strip() != 'qstat: Unknown Job Id ' + self.jobid

class Distributor:
	
	SLEEP = 30.0
	
	def __init__(self, max_jobs, sleep=SLEEP):
		""" Initialise the Distributor to run, at most, max_jobs and wait sleep
		   sleep seconds between checking if any jobs are finished.
		"""
		self.__max_jobs = max_jobs
		self.__inputs = []
		self.__sleep = sleep
	
	def distribute(self, n_jobs, indir, label, args):
		""" Distributes the n_jobs "super jobs" on the cluster. The executable
		   specified in args[0] is run on each file in indir. Any occurance of
		   the string "@@" in the arguments is replaced with the file name.
		"""
		timestamp = time.strftime('%y%m%d_%H%M%S')
		
		# Create timestamped job and log directories
		t_jobdir = os.path.join(cluster.jobdir,
		                        os.path.basename(args[0].split()[0]),
		                        timestamp)
		os.makedirs(t_jobdir)
		t_logdir = os.path.join(cluster.logdir,
		                        os.path.basename(args[0].split()[0]),
		                        timestamp)
		os.makedirs(t_logdir)
		
		# Partition the jobs into n_jobs jobs.
		tmpdir = self.__allocate(indir, n_jobs)
		
		# Create all the jobs.
		if label == '':
			label = os.path.basename(args[0])
		filenames = sorted(os.listdir(tmpdir))
		jobs = [ClusterJob(label, args, i, t_logdir) for i in xrange(len(filenames))]
		del filenames
		
		# Track the running jobs in an array.
		running_jobs = self.__max_jobs * [None]
		if self.__max_jobs == 0:
			running_jobs = len(jobs) * [None]
		
		# Submit jobs to the cluster.
		current_job = 0
		started_jobs = 0
		stopped_jobs = 0
		while stopped_jobs < len(jobs):
			if running_jobs[current_job] != None and\
			   not jobs[running_jobs[current_job]].isAlive():
				when = time.strftime('%d/%m/%y %H:%M:%S')
				print ' stopping job %d (%s)'%(running_jobs[current_job],when)
				stopped_jobs += 1
				running_jobs[current_job] = None
			
			if running_jobs[current_job] == None and\
			   started_jobs < len(jobs):
				when = time.strftime('%d/%m/%y %H:%M:%S')
				print 'starting job %d (%s)'%(started_jobs,when)
				running_jobs[current_job] = started_jobs
				jobs[started_jobs].start()
				started_jobs += 1
			
			current_job += 1
			if current_job >= len(running_jobs):
				current_job = 0
				time.sleep(self.__sleep)
		
		# Cleanup
		for filename in os.listdir(tmpdir):
			os.remove(os.path.join(tmpdir, filename))
		os.rmdir(tmpdir)
		
		return t_jobdir
	
	def __allocate(self, indir, n_jobs):
		""" Partitions the jobs into "super jobs". If no number is specified,
		   the same number of super jobs as jobs is created effectively changing
		   nothing.
		"""
		filenames = os.listdir(indir)
		if n_jobs == 0 or n_jobs > len(filenames):
			n_jobs = len(filenames)
		
		tmpdir = tempfile.mkdtemp(dir=os.path.join(os.environ['HOME'], 'tmp'))
		for i in xrange(n_jobs):
			outfile = open(os.path.join(tmpdir, str(i)), 'w')
			outfile.write('\n'.join([os.path.join(indir, filename)
			 for filename in filenames[(i+0)*len(filenames)/n_jobs:\
			  (i+1)*len(filenames)/n_jobs]]))
			outfile.close()
		
		return tmpdir

def main(argv = None):
	if argv == None:
		argv = sys.argv
	
	i = 1
	while i < len(argv) and argv[i].startswith('-'):
		i += 2
	
	parser = OptionParser(usage=USAGE)
	parser.add_option('-l', '--label',
	                  action='store', type='string', dest='label',
	                  default='',
	                  help='The label that the jobs will have.')
	parser.add_option('-n', '--njob',
	                  action='store', type='int', dest='n_jobs',
	                  default=0,
	                  help='The number of jobs to run.')
	parser.add_option('-m', '--mjob',
	                  action='store', type='int', dest='m_jobs',
	                  default=0,
	                  help='The maximum number of simultaneous jobs.')
	parser.add_option('-i', '--indir',
	                  action='store', type='string', dest='indir',
	                  help='The directory with the different files to use.')
	parser.add_option('-s', '--sleep',
	                  action='store', type='float', dest='sleep',
	                  default=Distributer.SLEEP,
	                  help='How long to sleep between checking.')
	options, args = parser.parse_args(argv[1:i])
	
	if not options.indir:
		parser.error('Input directory not defined.')
	
	tool = Distributor(options.m_jobs, options.sleep)
	tool.distribute(options.n_jobs, options.indir, options.label, argv[i:])
	
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))

