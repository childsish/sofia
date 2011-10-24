class Job(object):
	def __init__(self, cmd, stdin=None, stdout=None):
		self.cmd = cmd
		self.stdin = stdin
		self.stdout = stdout

