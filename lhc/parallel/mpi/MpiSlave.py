#!/usr/bin/python

from mpi4py import MPI
from subprocess import Popen, PIPE
from tags import master, slave

class Slave:
	def __init__(self, tag=None):
		self.__tag = tag
		if tag == None:
			self.__tag = MPI.ANY_TAG
	
	def start(self):
		""" Starts the loop. Calls run until kill signal is set."""
		comm = MPI.Comm.Get_parent()
		rank = comm.Get_rank()
		status = MPI.Status()
		while True:
			comm.send([rank], tag=slave.AVAILABLE)
			args = comm.recv(tag=self.__tag, status=status)
			if status.tag == master.DIE:
				break
			comm.send(self.run(args), tag=slave.RESULTS)
		comm.send([rank], tag=slave.DEAD)
	
	def run(self, args):
		""" The main method for the slave. Should be overridden in subclasses. """
		try:
			prc = Popen(args, stdout=PIPE, stderr=PIPE)
			stdout, stderr = prc.communicate()
			return [stdout, stderr]
		except Exception, e:
			import traceback
			traceback.print_exc()
			return ['', e]

def main(argv):
	slave = Slave()
	slave.start()

if __name__ == '__main__':
	import sys
	sys.exit(main(sys.argv))

