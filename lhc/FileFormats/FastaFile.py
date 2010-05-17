#!/usr/bin/python
#TODO: If FastaFile.close() or FastaFile.__del__() is called, close/delete the underlying file and turn IndexedEntrys into DirectEntrys.
# Do this by implementing a EntryInterface with an underlying implementation (DirectEntry, IndexedEntry).
# A bad idea? What happens with very big files?

import itertools
import os
import sys
import shutil

class Entry:
	""" An indexed entry into a fasta file.
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
		seq = self.getSeq()
		
		res = self.getHdr() + '\n'
		i = 0
		while i < len(seq):
			res += seq[i:i+self.__src.wrap] + '\n'
			i += self.__src.wrap
		return res
	
	def __getitem__(self, key):
		""" Returns a sliced IndexedEntry. """
		if isinstance(key, slice):
			return Entry(self.__src, self.__idx, key.start, key.stop - key.start)

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

	def getHdr(self):
		""" Returns the header. """
		self.__src.seek(self.__idx)
		return self.__src.readline().strip()

	def getSeq(self, fr = 0, sz = sys.maxint):
		""" Returns a sequence starting at fr which is as large as sz. """
		res = []
		wrap = self.__src.wrap # Get the wrap size from the source fasta file information.
		newlines = self.__src.newlines # Get the newline from the source fasta file information.
		
		fr = fr + self.__fr # Set starting point for index.
		if sz > self.__sz: # If we're trying to grab a sequence bigger than the one in the entry, truncate it.
			sz = self.__sz

		#offset = fr/wrap*(wrap+len(newlines)) + fr%wrap # Jump to correct line then correct column.
		#offset = int(float(fr)/wrap*(wrap + len(newlines))) # Try to jump straight to correct offset.
		offset = fr + (fr/wrap)*len(newlines) # Jump to incorrect offset then correct for newlines.
		if fr%wrap == 0:
			offset -= len(newlines)

		self.__src.seek(self.__idx) # Move index to the beginning of the entry.
		self.__src.readline() # Skip over the defline.
		self.__src.tell() # Needed to correct offset for PC format files (newlines = '\r\n'). I have no idea why.
		self.__src.seek(offset, 1) # Move index to starting point in sequence.

		# Keep appending sequence until the length of the resulting sequence is = sz.
		line = self.__src.readline()
		cSz = 0
		while line != '' and line[0] != '>' and cSz <= sz:
			res.append(line.strip())
			cSz += len(line.strip())
			line = self.__src.readline()

		return ''.join(res)[0:sz] # Efficient string concatenation and cut off any extra sequence.

class FastaFile:
	""" An indexed fasta file.  """
	
	DEFAULT_REGX = r'^>(?P<key>\w+)'
	
	class FastaFileHandle(file):
		""" Information about the source fasta file.
			Encoding, wrap size, etc...
		"""

		def __init__(self, src, regx):
			file.__init__(self, src, 'rU')
			fiftylines = [self.readline().strip() for i in itertools.repeat(None, 50)]
			self.wrap = max([len(line) for line in fiftylines if line[0] != '>'])
			self.seek(0)
			
			self.regx = regx

	def __init__(self, index_name, regx_string = ''):
		""" Create an indexed fasta file.
		    keys for regx_string must be:
		     key: main key
		     org: organism name
		     gi: Genbank gene identifier
		"""
		import cPickle
		import re
		
		regx = re.compile(regx_string)
		if regx_string == '':
			regx = re.compile(FastaFile.DEFAULT_REGX)
		
		# Get source file
		idx = open(index_name, 'rb')
		self.__mod = cPickle.load(idx)
		self.__src = FastaFile.FastaFileHandle(cPickle.load(idx), regx)
		idxs = cPickle.load(idx)
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
		""" Number of entries in the fasta file. """
		return len(self.__lst)

	def __getitem__(self, key):
		""" Retrieve an entry from the fasta file.
			The key can be an index or an accession.
		"""
		if isinstance(key, str):
			return self.__lst[self.__dct[key]]
		elif isinstance(key, int):
			return self.__lst[key]
		elif isinstance(key, slice):
			pass  # FIXME: implement slicing a fasta file
		raise IndexError(str(key) + ' is out of range.')

	def __iter__(self):
		return self.__lst.__iter__()

	def __contains__(self, item):
		""" Check to see if an accession or Entry exists in the fasta file.
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

def splitFasta(infname, npart, outdname=None):
	if outdname == None:
		import tempfile
		outdname = tempfile.mkdtemp()
	elif not os.path.exists(outdname):
		os.makedirs(outdname)
	
	infile = open(infname)
	i = -1
	outs = []
	for line in infile:
		if line.startswith('>'):
			i = (i+1)%npart
			if i == len(outs):
				outfile = open(os.path.join(outdname, '%s.fasta'%(i)), 'w')
				outs.append(outfile)
		outs[i].write(line)
	infile.close()
	for outfile in outs:
		outfile.close()
	
	return (outdname, [outfile.name for outfile in outs])

def writeFasta(ents, fname, width=0):
	outfile = open(fname, 'w')
	if width == 0:
		for ent in ents:
			outfile.write('>%s\n%s\n'%(ent))
	else:
		for hdr, seq in ents:
			outfile.write('>%s\n'%hdr)
			for i in xrange(0, len(seq), width):
				outfile.write(seq[i:i+width])
				outfile.write('\n')
	outfile.close()

def readFasta(fname):
	res = []
	infile = open(fname)
	hdr = None
	seq = None
	for line in infile:
		if line[0] == '>':
			if hdr != None:
				res.append((hdr, ''.join(seq)))
			hdr = line[1:].strip()
			seq = []
		else:
			seq.append(line.strip())
	res.append((hdr, ''.join(seq)))
	return res

def iterFasta(fname):
	infile = open(fname)
	hdr = None
	seq = None
	for line in infile:
		if line[0] == '>':
			if hdr != None:
				yield (hdr, ''.join(seq))
			hdr = line[1:].strip()
			seq = []
		else:
			seq.append(line.strip())
	yield (hdr, ''.join(seq))
	infile.close()

def index_file(filename, index_name = None):
	import cPickle
	import stat
	
	if index_name == None:
		if '.' in filename:
			index_name = filename[:filename.rfind('.')] + '.idx'
		else:
			index_name = filename + '.idx'
	
	if os.path.exists(index_name):
		try:
			infile = open(index_name)
			iMod = cPickle.load(infile) # Indexed modification time.
			infile.close()
			
			cMod = os.stat(filename)[stat.ST_MTIME] # Current modification time.

			if iMod == cMod:
				return index_name
		except EOFError, e: # If the file is empty then continue anyway.
			pass
	
	lst = []
	infile = open(filename, 'rb')
	while True: # Equivalent of do-while loop.
		idx = infile.tell()
		line = infile.readline()

		if len(line) <= 0: # Exit condition
			break
		elif line[0] == '>':
			lst.append(idx)

	# Pickle the index to improve file access speed.
	outfile = file(index_name, 'wb')
	cPickle.dump(os.stat(filename)[stat.ST_MTIME], outfile, cPickle.HIGHEST_PROTOCOL)
	cPickle.dump(filename, outfile, cPickle.HIGHEST_PROTOCOL)
	cPickle.dump(lst, outfile, cPickle.HIGHEST_PROTOCOL)
	outfile.close()
	
	return index_name

def flatten_file(infname):
	from tempfile import mkstemp
	outfile, outfname = mkstemp()
	for hdr, seq in iterFasta(infname):
		os.write(outfile, '>%s\n%s\n'%(hdr, seq))
	os.close(outfile)
	shutil.move(outfname, infname)

def main(argv = None):
	if argv == None:
		argv = sys.argv
	
	if argv[1] == 'index':
		index_file(argv[2])
	elif argv[1] == 'flatten':
		flatten_file(argv[2])
	else:
		print 'Argument 1 must be either index or flatten'

if __name__ == '__main__':
	sys.exit(main(sys.argv))
