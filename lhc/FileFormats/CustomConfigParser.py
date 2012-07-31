from ConfigParser import ConfigParser

class CustomConfigParser(ConfigParser):
	def __init__(self):
		ConfigParser.__init__(self)
	
	def add_option(self, section, option, action='store', type='string', nargs=1,
	 choices=None):
		 