import sys

from paths import cluster
from subprocess import Popen, PIPE

class PbsJob:
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
