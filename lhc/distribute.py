#!/usr/bin/python

from collections import deque
import os
import threading
import time

NPRC = 4
if 'NUMBER_OF_PROCESSORS' in os.environ:
        NPRC = int(os.environ['NUMBER_OF_PROCESSORS'])
		
		import sys
		sys.platform

class Job(threading.Thread):
	
	def __init__(self, fn, args):
		threading.Thread.__init__(self)
		
		self.__fn = fn
		self.__args = args
		self.__res = None
		self.__error = None
	
	def run(self):
		try:
			self.__res = self.__fn(self.__args)
		except Exception, e:
			import traceback
			print self.getName()
			traceback.print_exc()
			self.__error = e
	
	def getResult(self):
		return self.__res
	
	def getError(self):
		return self.__error

def distribute(jobfn, args, resfn = None):
	res = len(args) * [None]
	
	threads = [None for i in range(NPRC)]
	
	i = 0
	started = 0
	stopped = 0
	while stopped < len(args):
		if threads[i] != None and not threads[i][1].isAlive():
			if threads[i][1].getError() != None:
				raise threads[i][1].getError()
			res[threads[i][0]] = threads[i][1].getResult()
			stopped += 1
			#print str(stopped) + '/' + str(len(args)) + ' ' + str(time.time() - threads[i][2])
			threads[i] = None
		
		if threads[i] == None:
			if started < len(args):
				threads[i] = (started, Job(jobfn, args[started]), time.time())
				threads[i][1].start()
				started += 1
		
		time.sleep(0.5)
		
		i += 1
		if i >= NPRC:
			i = 0
	
	if resfn != None:
		return resfn(res)
	return res
