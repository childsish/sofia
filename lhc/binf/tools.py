import sys
import os

class ConfigParser:
	
	DEFAULT_COMMANDS = (str, 'store', None)
	
	def __init__(self):
		self.__commands = {}
		self.__sections = {}
	
	def add_option(self, section, option, type=str, action='store', nargs=None):
		if hasattr(type, '__iter__') and nargs == None:
			nargs = len(type)
		self.__commands.setdefault(section, {})
		self.__commands[section][option] = (type, action, nargs)
	
	def read(self, fname):
		overwrite = set()
		for section in self.__sections:
			for key in self.__sections[section]:
				if isinstance(self.__sections[section][key], list):
					overwrite.add((section, key))
		
		typ, action, nargs = ConfigParser.DEFAULT_COMMANDS
		
		infile = open(fname)
		for line in infile:
			if line.strip().startswith('#'):
				continue
			elif line.startswith('['):
				section = line.strip()[1:-1]
				self.__sections.setdefault(section, {})
			elif len(line.strip()) > 0:
				key = line[:line.find(':')]
				val = line[line.find(':') + 2:].strip()
				if section in self.__commands and key in self.__commands[section]:
					typ, action, nargs = self.__commands[section][key]
				else:
					typ, action, nargs = ConfigParser.DEFAULT_COMMANDS
				
				# Break down the value if several values expected.
				if nargs != None:
					val = val.split()
					if len(val) != nargs:
						raise Exception('Expected %d arguments in section %s option %s.'
						 ' Got %d.'%(nargs, section, key, len(val)))
					
					if hasattr(typ, '__iter__'):
						if len(typ) != nargs:
							raise Exception('Expected %d types in section %s option %s.'
							' Got %d.'%(nargs, section, key, len(typ)))
						val = [typ[i](val[i]) for i in xrange(nargs)]
					else:
						val = map(typ, val)
				else:
					val = typ(val)
				
				if action == 'store':
					self.__sections[section][key] = val
				elif action == 'append':
					if (section, key) in overwrite:
						self.__sections[section][key] = []
						overwrite.remove((section, key))
					self.__sections[section].setdefault(key, [])
					self.__sections[section][key].append(val)
		infile.close()
	
	def sections(self):
		return self.__sections.keys()
	
	def has_section(self, section):
		return section in self.__sections
	
	def options(self, section):
		return self.__sections[section].keys()
	
	def has_option(self, section, option):
		return section in self.__sections and option in self.__sections[section]
	
	def get(self, section, option):
		return self.__sections[section][option]
	
	def items(self, section):
		return self.__sections[section].items()
	
	def set(self, section, option, value):
		self.__sections.setdefault(section, {})
		self.__sections[section][option] = value

def argsort(seq):
	return sorted(range(len(seq)), key=seq.__getitem__)

def loadPlugins(indir, cls):
	sys.path.append(indir)
	plugins = []
	
	mnames = [fname[:-3] for fname in os.listdir(indir)\
	 if fname[0] != '.' and fname.endswith('.py')]
	
	for mname in mnames:
		d = __import__(mname).__dict__
		
		for k, v in d.iteritems():
			if k == cls.__name__:
				continue
			
			try:
				if issubclass(v, cls):
					plugins.append(v)
			except TypeError:
				continue
	
	return plugins
