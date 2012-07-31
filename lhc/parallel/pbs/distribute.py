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

import numpy
import os
import re
import sys
import tempfile
import time

from argparse import ArgumentParser
from ConfigParser import ConfigParser
from operator import mul
from paths import cluster
from string import Template
from subprocess import Popen, PIPE
from itertools import product, izip

USAGE = """usage: %prog [options] executable [executable_args]"""

class ClusterJob:
	def __init__(self, label, args, logdir):
		self.label = label
		self.args = args
		self.jobid = None
		self.logdir = logdir

	def __del__(self):
		if self.jobid != None and self.isAlive():
			prc = Popen([cluster.qdel, self.jobid], stdout=PIPE, stderr=PIPE)
			stdout, stderr = prc.communicate()
			sys.stdout.write(stdout)
			sys.stderr.write(stderr)
	
	def start(self):
		prc = Popen([cluster.qsub,
		             '-o', self.logdir,
		             '-e', self.logdir,
		             '-N', self.label,
		             '-v', self.args,
		             cluster.pbs_slave],
		            stdout=PIPE, stderr=PIPE)
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

class Argument(object):
	def __iter__(self):
		return self
	
	def next(self):
		raise NotImplementedError()

class ArgumentRange(Argument):
	def __init__(self, fr, to, st, fmt):
		self.__fmt = fmt
		self.__rng = numpy.arange(fr, to, st)
	
	def __len__(self):
		return len(self.__rng)
	
	def __iter__(self):
		return (self.__fmt%(val,) for val in self.__rng)

class ArgumentList(Argument):
	def __init__(self, lst):
		self.__lst = lst
		self.__idx = 0
	
	def __len__(self):
		return len(self.__lst)
	
	def next(self):
		if self.__idx >= len(self.__lst):
			raise StopIteration()
		res = self.__lst[self.__idx]
		self.__idx += 1
		return res

class ArgumentDirectory(ArgumentList):
	def __init__(self, indir, full):
		if full:
			lst = [os.path.join(indir, fname) for fname in os.listdir(indir)]
		else:
			lst = os.listdir(indir)
		ArgumentList.__init__(self, lst)

class CommandLineGenerator(object):

	REGX = re.compile(':[_a-zA-Z][_a-zA-Z0-9]*')

	def __init__(self, args):
		#TODO: Use an ordered dictionary when it's available for python.
		self.arglist = args
		self.__argdict = dict(((arg, None) for arg in args
		 if CommandLineGenerator.REGX.match(arg)))
		#TODO: Check for reserved key words ie. 1, 2, 3, 4...
		# (Only when implementing a config file)
		self.__ckw = 1
	
	def __len__(self):
		if len(self.arglist) == 0:
			return 0
		if len(self.__argdict) == 0:
			return 1
		return reduce(mul, (len(gen) for gen in self.__argdict.itervalues()))
	
	def __nextKeyword(self):
		kw = ':%d'%(self.__ckw,)
		self.__ckw += 1
		if kw not in self.arglist:
			self.arglist.append(kw)
		return kw
	
	#def read(self, fname):
		#raise NotImplementedError()
		#parser = ConfigParser()
		#parser.read(fname)
		#for section in parser.sections():
			#typ = parser.get(section, 'type')
			#kw = None
			#if parser.has_option(section, 'keyword'):
				#kw = parser.get(section, 'keyword')
			
			#if typ == 'range':
				#fmt = '%f'
				#if parser.has_option(section, 'format'):
					#fmt = parser.get(section, 'format')
				#self.addRange(float(parser.get(section, 'from')),
				 #float(parser.get(section, 'to')),
				 #float(parser.get(section, 'step')),
				 #fmt, kw)
			#elif typ == 'list':
				#lst = [val for key, val in parser.items(section)
				 #if key != 'list']
				#self.addList(lst, kw)
			#elif typ == 'directory':
				#self.addDirectory(parser.get(section, 'dname'),
				 #bool(parser.get(section, 'full')), kw)
	
	#def setArgumentList(self, args):
		#self.arglist = args
	
	def addArgument(self, arg, kw=None):
		if kw == None:
			kw = self.__nextKeyword()
		self.__argdict[kw] = arg
	
	def addRange(self, fr, to, step, fmt='%f', kw=None):
		self.addArgument(ArgumentRange(fr, to, step, fmt), kw)
	
	def addList(self, lst, kw=None):
		self.addArgument(ArgumentList(lst), kw)
	
	def addDirectory(self, indir, full=True, kw=None):
		self.addArgument(ArgumentDirectory(indir, full), kw)
	
	def generateArguments(self):
		if len(self) == 0:
			return
		
		keys = sorted(self.__argdict, key=lambda x:self.arglist.index(x))
		vals = [self.__argdict[key] for key in keys]
		for arglist in product(*vals):
			argdict = dict(izip(keys, arglist))
			args = []
			for arg in self.arglist:
				if arg in argdict:
					val = argdict[arg]
				else:
					val = arg
				
				if hasattr(val, '__iter__'):
					args.extend(val)
				else:
					args.append(val)
			yield (args, arglist)

class Distributor:
	
	SLEEP = 30.0
	
	def __init__(self, max_jobs, sleep=SLEEP):
		""" Initialise the Distributor to run, at most, max_jobs and wait sleep
		   sleep seconds between checking if any jobs are finished.
		"""
		self.__max_jobs = max_jobs
		self.__inputs = []
		self.__sleep = sleep
	
	def distribute(self, cmdgen, n_jobs=None, label=None):
		""" Distributes the n_jobs "super jobs" on the cluster. Each command line generated by
		 cmdgen is run on a cluster node. The number of jobs to be run is limited by n_jobs and
		 each job is given the name of the executable if no label is supplied.
		"""
		timestamp = time.strftime('%y%m%d_%H%M%S')
		
		# Create timestamped job and log directories
		if label == None:
			label = os.path.basename(cmdgen.arglist[0])
		t_jobdir = os.path.join(cluster.jobdir, label, timestamp)
		os.makedirs(t_jobdir)
		t_logdir = os.path.join(cluster.logdir, label, timestamp)
		os.makedirs(t_logdir)
		
		#  A dirty hack just to get things working for now. I need a way to map the
		# filename to the arguments. Otherwise I'm trying to write filenames that are
		# too long.
		outfile = open(os.path.join(cluster.jobdir, label, '%s.map'%(timestamp,)), 'w')
		if n_jobs == None:
			tmpdir = None
			# Create all the jobs.
			jobs = []
			c_job = 0
			for args, arglist in cmdgen.generateArguments():
				jobs.append(ClusterJob(label, self.formatArgs(args,
				 lc_jobdir=t_jobdir,
				 lc_filename=str(c_job),
				 lc_superjob='0'), t_logdir))
				outfile.write('%d\t%s\n'%(c_job, '\t'.join(map(str, arglist))))
				c_job += 1
			#jobs = [ClusterJob(label,
			#  self.formatArgs(args,
			#   lc_jobdir=t_jobdir,
			#   lc_filename='.'.join(map(os.path.basename, arglist)),
			#   lc_superjob='0'),
			#  t_logdir)
			# for args, arglist in cmdgen.generateArguments()]
		else:
			raise NotImplementedError('This functionality has been disabled for now')
			# Partition the jobs into n_jobs jobs.
			tmpdir = self.__allocate(cmdgen, n_jobs)
			filenames = os.listdir(tmpdir)
		
			# Create all the jobs.
			jobs = [ClusterJob(label,
			  self.formatArgs(args,
			   lc_jobdir=t_jobdir,
			   lc_filename=os.path.join(tmpdir, filenames[i]),
			   lc_superjob='1'),
			  t_logdir)
			 for i in xrange(len(filenames))]
			del filenames
		outfile.close()
		
		# Track the running jobs in an array.
		if self.__max_jobs == None:
			running_jobs = len(jobs) * [None]
		else:
			running_jobs = self.__max_jobs * [None]
		
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
		if tmpdir:
			for filename in os.listdir(tmpdir):
				os.remove(os.path.join(tmpdir, filename))
			os.rmdir(tmpdir)
		
		return t_jobdir
	
	def formatArgs(self, args, **kw):
		""" Formats the arguments into a single string to be passed to the
		   argument of qsub that sets the environment variable. I don't know of
		   any other way to send arguments to a script on the cluster.
		"""
		args = ['lc_arg%02d="%s"'%(i, args[i]) for i in xrange(len(args))]
		args += ['%s="%s"'%(k,str(v)) for k, v in kw.iteritems()]
		return ','.join(args)
	
	def __allocate(self, cmdgen, n_jobs):
		""" Partitions the jobs into "super jobs". If no number is specified,
		   the same number of super jobs as jobs is created effectively changing
		   nothing.
		"""
		tmpdir = tempfile.mkdtemp(dir=os.path.join(os.environ['HOME'], 'tmp'))
		i = 0
		outs = []
		for args, arglist in cmdgen.generateArguments():
			if (i%n_jobs) == len(outs):
				outfile = open(os.path.join(tmpdir, '%d'%(i%n_jobs,)), 'w')
				outs.append(outfile)
			outfname = '.'.join(map(os.path.basename, arglist))
			outfname = outfname.replace('/', '_')
			outs[i%n_jobs].write('%s\t%s\n'%(outfname, ' '.join(args)))
			i += 1
		for outfile in outs:
			oufile.close()
		
		return tmpdir

def arg_range_adaptor(arg):
	if arg[0] == 'r':
		arg = arg[1:]
	fr, to, step, fmt = arg.split(',')
	return ArgumentRange(float(fr), float(to), float(step), fmt)

def arg_list_adaptor(arg):
	return ArgumentList(arg.split(','))

def arg_directory_adaptor(arg):
	return ArgumentDirectory(arg, True)

def arg_file_adaptor(arg):
	infile = open(arg)
	lst = [line.strip().split() for line in infile]
	infile.close()
	return ArgumentList(lst)

def main(argv = None):
	if argv == None:
		argv = sys.argv
	
	i = 1
	while i < len(argv) and argv[i].startswith('-'):
		i += 2
	
	parser = ArgumentParser()
	parser.add_argument('-l', '--label',
	 action='store', dest='label',
	 help='The label that the jobs will have.')
	parser.add_argument('-m', '--mjob',
	 action='store', type=int, dest='m_jobs',
	 help='The maximum number of simultaneous jobs.')
	parser.add_argument('-n', '--njob',
	 action='store', type=int, dest='n_jobs',
	 help='The number of jobs to run.')
	parser.add_argument('-s', '--sleep',
	 action='store', type=float, dest='sleep',
	 default=Distributor.SLEEP,
	 help='How long to sleep between checking.')
	#parser.add_argument('-c', '--config',
	 #action='store', dest='config',
	 #help='A configuration file for dealing with ranges of input')
	parser.add_argument('-R', '--range', metavar='FROM,TO,STEP,FORMAT',
	 action='append', type=arg_range_adaptor, dest='args',
	 help='The start, stop and step values of a range. The format is also necessary.')
	parser.add_argument('-L', '--list', metavar='LIST',
	 action='append', type=arg_list_adaptor, dest='args',
	 help='A comma seperated list')
	parser.add_argument('-D', '--directory', metavar='DIRECTORY',
	 action='append', type=arg_directory_adaptor, dest='args',
	 help='The directory with the different files to use.')
	parser.add_argument('-F', '--file', metavar='FILE',
	 action='append', type=arg_file_adaptor, dest='args',
	 help='A file with argument parameters. Each line will be directly inserted into the '\
	  'command line')
	parser.add_argument('command',
	 help='The command to execute on the cluster')
	args = parser.parse_args(argv[1:i+1])
	
	if args.args == None:
		parser.error('No arguments were specified for cluster job. Use qsub directly instead.')
	
	cmdgen = CommandLineGenerator(argv[i:])
	#if args.config:
		#cmdgen.read(args.config)
	for arg in args.args:
		cmdgen.addArgument(arg)
	
	tool = Distributor(args.m_jobs, args.sleep)
	tool.distribute(cmdgen, args.n_jobs, args.label)
	
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))

