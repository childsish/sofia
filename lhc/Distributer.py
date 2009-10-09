#!/usr/bin/python

import threading
import time
import sys

class ClusterJob(threading.Thread):
	def __init__(self, fn, args):
		threading.Thread.__init__(self)
		self.fn = fn
		self.args = args
		self.res = len(self.args) * [None]
		self.err = None
		self.started = None
	
	def run(self):
		try:
			for i in xrange(len(self.args)):
				self.res[i] = self.fn(*self.args[i])
		except Exception, e:
			import traceback
			print self.getName()
			traceback.print_exc()
			self.error = e
	
	def getResult(self):
		return self.res
	
	def getError(self):
		return self.err

class Distributer:

	SLEEP = 5.0
	TIMEOUT = 20.0

	def __init__(self, max_jobs=None, sleep=SLEEP, timeout=TIMEOUT):
		if max_jobs == None:
			max_jobs = self.__getNumberOfProcessors()
		self.__max_jobs = max_jobs
		self.__inputs = []
		self.__sleep = sleep
		self.__timeout = timeout
	
	def distribute(self, fn, args, n_jobs=0):
		argss = self.__allocate(args, n_jobs)
		
		jobs = [ClusterJob(fn, argss[i]) for i in xrange(len(argss))]
		
		running_jobs = self.__max_jobs * [None]
		
		current_job = 0
		started_jobs = 0
		stopped_jobs = 0
		while stopped_jobs < len(jobs):
			when = time.time()
			when_str = time.strftime('%d/%m/%y %H:%M:%S', time.localtime(when))
			
			if running_jobs[current_job] != None and\
			   not jobs[running_jobs[current_job]].isAlive():
				print ' Stopping job %d (%s)'%(running_jobs[current_job], when_str)
				stopped_jobs += 1
				running_jobs[current_job] = None
			#elif running_jobs[current_job] != None and\
			   #when - jobs[running_jobs[current_job]].started > self.__timeout:
				#print ' Restarting job %d (%s)'%(running_jobs[current_job], when_str)
				#job_idx = running_jobs[current_job]
				#jobs[job_idx] = ClusterJob(fn, argss[job_idx])
				#jobs[job_idx].start()
				#jobs[job_idx].started = when
			
			if running_jobs[current_job] == None and\
			   started_jobs < len(jobs):
				
				print 'Starting job %d (%s)'%(started_jobs, when_str)
				running_jobs[current_job] = started_jobs
				jobs[started_jobs].start()
				jobs[started_jobs].started = when
				started_jobs += 1
			
			current_job += 1
			if current_job >= self.__max_jobs:
				current_job = 0
				time.sleep(self.__sleep)
		
		res = []
		for job in jobs:
			res += job.res
		return res

	def __allocate(self, args, n_jobs):
		if n_jobs == 0 or n_jobs > len(args):
			n_jobs = len(args)
		
		tmpdir = []
		for i in xrange(n_jobs):
			tmpdir.append(args[(i+0)*len(args)/n_jobs:
			                   (i+1)*len(args)/n_jobs])
		
		return tmpdir
	
	def __getNumberOfProcessors(self):
		count = 0
		if 'linux' in sys.platform:
			infile = open('/proc/cpuinfo')
			for line in infile:
				if line.startswith('processor'):
					count += 1
			infile.close()
		elif 'win32' in sys.platform:
			count = int(os.environ['NUMBER_OF_PROCESSORS'])
		else:
			count = 1
			print 'Unable to count processors for ' + sys.platform
			print '. Contact Liam!' 
		return count
