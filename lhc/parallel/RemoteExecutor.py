import getpass
import os
import paramiko

class RemoteExecutor(Executor):
	
	REMOTE_SERVERS = {}
	
	@classmethod
	def registerServer(cls, server, username=None):
		if username == None:
			username = getpass.getuser()
		password = getpass.getpass("%s@%s's password: "%(username, server))
		ssh = paramiko.SSHClient()
		ssh.connect(server, username=username, password=password)
		RemoteExecutor.REMOTE_SERVERS[server] = ssh

