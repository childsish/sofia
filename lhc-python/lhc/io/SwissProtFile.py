import os
import sys

class Entry:
	""" An indexed entry into a swissprot file.
		Currently unsure whether this will work on different platforms.
		The source information is shared - Don't delete it before you are finished with the entries.
	"""
	
	def __init__(self, src, idx, fr = 0, sz = sys.maxint):
		""" Intialises the entry. """
		self.__src = src # Source file info. Not to be touched by anything...
		self.__idx = idx
		self.__fr = fr
		self.__sz = sz
	
	def __str__(self):
		""" Print the entry. """
		res = []
		
		self.__src.seek(self.__idx)
		for line in self.__src:
			res.append(line)
			if line[:2] == '//':
				break
		
		return ''.join(res)
	
	def __getitem__(self, key):
		""" Returns a sliced IndexedEntry. """
		if len(key) > 2:
			raise KeyError('Invalid key: ' + key)
		
		res = []
		
		self.__src.seek(self.__idx)
		for line in self.__src:
			if line[:2] == '//':
				break
			elif line[:2] == key:
				res.append(line[5:].strip())
		
		if len(res) == 0:
			raise IndexError('Index out of bounds: ' + key)
		
		return res
	
	def __contains__(self, key):
		self.__src.seek(self.__idx)
		for line in self.__src:
			if line[:2] == '//':
				break
			elif line[:2] == key:
				return True
		return False
	
	def getAcc(self):
		""" Returns the accession number. """
		self.__src.seek(self.__idx)
		line = self.__src.readline().strip()
		match = self.__src.regx.search(line)
		if not match:
			raise Exception('Unable to match defline: ' + line) #FIXME: Raise a better error.
		elif match.group('key') == None:
			raise Exception('Unable to match capturing group "key" in regex: ' + self.__src.regx.pattern) #FIXME: Raise a better error.
		return match.group('key')

	def getSeq(self):
		""" Returns the sequence. """
		res = []
		
		self.__src.seek(self.__idx)
		flag = False
		for line in self.__src:
			if line[:2] == '//':
				break
			elif line[:2] == 'SQ':
				flag = True
			elif flag:
				res.append(line.split())
		
		return ''.join([''.join(r) for r in res])

class SwissProtFile:
	""" An indexed swissprot file.  """
	
	DEFAULT_REGX = r'^ID   (?P<key>\w+)'
	
	class SwissProtFileHandle(file):
		""" Information about the source fasta file.
			Encoding, wrap size, etc...
		"""

		def __init__(self, src, regx):
			file.__init__(self, src, 'rU')
			
			self.regx = regx

	def __init__(self, index_name, regx_string = ''):
		""" Create an indexed fasta file.
		    keys for regx_string must be:
		     key: main key
		"""
		import cPickle
		import re
		
		regx = re.compile(regx_string) # Declare and define default.
		if regx_string == '':
			regx = re.compile(SwissProtFile.DEFAULT_REGX)
		
		# Get source file
		idx = open(index_name, 'rb')
		self.__mod = cPickle.load(idx) # Last modified
		self.__src = SwissProtFile.SwissProtFileHandle(cPickle.load(idx), regx) # Source file.
		idxs = cPickle.load(idx) # The indexes of each entry.
		idx.close()
		
		# Initialise list and dictionary.
		self.__lst = len(idxs) * [None] # The list of entries
		self.__dct = {} # The dictionary of accessions
		for i in xrange(len(idxs)):
			entry = Entry(self.__src, idxs[i])
			self.__lst[i] = entry
			self.__dct[entry.getAcc()] = i
		
		del idxs

	def __len__(self):
		""" Number of entries in the swissprot file. """
		return len(self.__lst)

	def __getitem__(self, key):
		""" Retrieve an entry from the swissprot file.
			The key can be an index or an accession.
		"""
		if isinstance(key, str):
			return self.__lst[self.__dct[key]]
		elif isinstance(key, int):
			return self.__lst[key]
		elif isinstance(key, slice):
			pass  # FIXME: implement slicing a swissprot file
		raise IndexError(str(key) + ' is out of range.')

	def __iter__(self):
		return self.__lst.__iter__()

	def __contains__(self, item):
		""" Check to see if an accession or Entry exists in the swissprot file.
			Can also be used to check to see if an index is in range.
		"""
		if isinstance(item, str):
			return item in self.__dct
		elif isinstance(item, int):
			return 0 <= item and item < len(self)
		elif isinstance(item, Entry):
			return item.getAcc() in self.__dct
		return False

	def has_key(self, key):
		return key in self

	def items(self):
		""" Cost: O(n) """
		return [(key, self.__lst[val]) for key, val in self.__dct.iteritems()]

	def keys(self):
		return self.__dct.keys()

	def values(self):
		return self.__lst
	
	def iteritems(self):
		return ((key, self.__lst[val]) for key, val in self.__dct.iteritems())

	def iterkeys(self):
		return self.__accs.iterkeys()

	def itervalues(self):
		return self.__lst.__iter__()

	def name(self):
		""" Returns the name of the underlying fasta file. """
		return self.__src.name

def index_file(filename, index_name=None):
	import cPickle
	import stat
	
	if index_name == None:
		index_name = filename[:filename.rfind('.')] + '.idx'
	
	if os.path.exists(index_name):
		try:
			infile = open(index_name)
			iMod = cPickle.load(infile) # Indexed modification time.
			infile.close()
			
			cMod = os.stat(filename)[stat.ST_MTIME] # Current modification time.

			if iMod == cMod:
				return
		except EOFError, e: # If the file is empty then continue anyway.
			pass
	
	lst = []
	infile = open(filename, 'rb')
	while True: # Equivalent of do-while loop.
		idx = infile.tell()
		line = infile.readline()

		if len(line) <= 0: # Exit condition
			break
		elif line[:2] == 'ID':
			lst.append(idx)

	# Pickle the index to improve file access speed.
	outfile = file(index_name, 'wb')
	cPickle.dump(os.stat(filename)[stat.ST_MTIME], outfile, cPickle.HIGHEST_PROTOCOL)
	cPickle.dump(filename, outfile, cPickle.HIGHEST_PROTOCOL)
	cPickle.dump(lst, outfile, cPickle.HIGHEST_PROTOCOL)
	outfile.close()

def main():
	if not os.path.exists(r'c:\lib\uniprot\uniprot_sprot.dat.idx'):
		index_file(r'c:\lib\uniprot\uniprot_sprot.dat', r'c:\lib\uniprot\uniprot_sprot.dat.idx')
	
	tool = SwissProtFile(r'c:\lib\uniprot\uniprot_sprot.dat.idx')
	print tool[5].getSeq()
	
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main())