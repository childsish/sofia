import os
import threading
from subprocess import Popen, PIPE

class CpuJob(threading.Thread):
	def __init__(self, args, jobdir, logdir, fname):
		threading.Thread.__init__(self)
		self.args = args
		self.jobdir = jobdir
		self.logdir = logdir
		self.fname = fname
	
	def run(self):
		# Each line in the file is a job to run.
		#print 'Printing output to %s'%(os.path.join(self.jobdir, self.fname),)
		prc_stdout = open(os.path.join(self.jobdir, self.fname), 'w')
		prc_stderr = open(os.path.join(self.logdir, self.fname), 'w')
		try:
			prc = Popen(self.args, stdout=prc_stdout, stderr=prc_stderr)
		except OSError, e:
			prc_stdout.close()
			os.remove(prc_stdout.name)
			print c_args
			raise e
		prc.wait()
		prc_stdout.close()

