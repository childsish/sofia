#!/usr/bin/python

import sys
import time
import threading

from mpi4py import MPI
from tags import master, slave
from Job import Job

class Master:
	def __init__(self):
		self.__len = 0

		self.__slaves = set()
		self.__free = []
		
		self.__waiting = []
		self.__complete = []
		
		self.__run = False

	def __len__(self):
		return self.__len
	
	def __del__(self):
		self.stop()

	def enqueue(self, args, tag=None):
		""" Submit a job to be processed. """
		if not self.__run:
			raise Exception('The master is dead.')
		
		if tag in [master.DIE, master.JOB]:
			raise Exception('Tag %d is reserved.'%(tag))
		elif tag == None:
			tag = master.JOB
		self.__waiting.append(Job(args, tag))
		self.__len += 1

	def dequeue(self):
		""" Get a finished job FIFO manner. An exception is raise if there are no jobs
		 currently being processed. Otherwise block until a result is ready. """
		if self.__len == 0:
			raise Exception('No jobs are being processed')
		else: # Block
			while self.__run and len(self.__complete) == 0:
				time.sleep(self.__sleep)

		self.__len -= 1
		return self.__complete.pop()
	
	def start(self, py, n_prcs, sleep=5.0):
		self.__comm = MPI.COMM_SELF.Spawn(sys.executable, args=[py], maxprocs=n_prcs)
		self.__sleep = sleep
		self.__updater = threading.Thread(None, self.__update)
		self.__updater.start()
		self.__run = True
	
	def stop(self):
		for slave in self.__slaves:
			self.enqueue(Job([], master.DIE))
		self.__run = False

	def getComplete(self):
		""" Returns the number of complete jobs. """
		return len(self.__complete)

	def __update(self):
		""" A loop which constantly submits pending jobs and pulls complete jobs
		 from the cluster. """
		while self.__run or len(self.__waiting) > 0:
			status = MPI.Status()
			data = self.__comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
			if status.tag == slave.AVAILABLE:
				if status.source not in self.__slaves:
					self.__slaves.add(status.source)
				self.__free.append(status.source)
			elif status.tag == slave.RESULTS:
				self.__complete.append(data)
			elif status.tag == slave.DEAD:
				print 'Slave dying'
				self.__slaves.remove(status.source)

			while len(self.__waiting) and len(self.__free) > 0:
				job = self.__waiting.pop()
				rank = self.__free.pop()
				self.__comm.send(job.args, dest=rank, tag=job.tag)

def main(argv):
	import random
	tool = Master()
	tool.start('slave.py', 8)
	for i in xrange(200):
		tool.enqueue(argv[1:])
	while len(tool) > 0:
		res = tool.dequeue()
		print res[0].strip()
		print res[1].strip()
	tool.stop()

if __name__ == '__main__':
	sys.exit(main(sys.argv))

