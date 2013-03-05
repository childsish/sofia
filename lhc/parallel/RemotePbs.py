import sys
import paramiko

from paths import cluster
from subprocess import Popen, PIPE

from RemoteExecutor import RemoteExecutor

class RemotePbs(RemoteExecutor):
	def __init__(self, base, server, label, args, logdir):
		self.__base = base
		self.__ssh = RemoteExecutor.REMOTE_SERVERS[server]
		
		self.label = label
		self.args = args
		self.jobid = None
		self.logdir = logdir

		self.
	
	def setupRemoteServer

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

	def startJob(self, job):
		ssh.execute('cd %s'%(self.__base))
	
	def isAvailable(self):
		raise NotImplementedError()
	
	def isFinished(self):
		raise NotImplementedError()

