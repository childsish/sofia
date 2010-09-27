#!/usr/bin/python

import os
import sys

class SynchError(Exception):
	def __init__(self, val):
		self.__val = val
	
	def __str__(self):
		return self.__val

class WrapError(Exception):
	def __init__(self, lineno, wrap):
		self.__lineno = lineno
		self.__wrap = wrap
	
	def __str__(self):
		return "Line number %d does not have %d characters"%(self.__lineno, self.__wrap)

class IndexedFastaSequence:
	""" An indexed sequence into a fasta file. Retrieving a sequence involves opening a file
		 finding the start and stop indices, returning the stripped and joined lines between
		 them and closing the file.
		Currently unsure whether this will work on different platforms.
	"""
	
	def __init__(self, fname, idx_fr, idx_to, wrap, newlines, seq_fr=0, seq_to=sys.maxint):
		""" Intialises the entry. """
		self.__fname = fname
		self.__idx_fr = idx_fr
		self.__idx_to = idx_to
		self.__wrap = wrap
		self.__newlines = newlines
		self.__seq_fr = seq_fr
		self.__seq_to = seq_to
	
	def __len__(self):
		return self.__seq_to - self.__seq_fr
	
	def __str__(self):
		offset_fr = self.__calcOffset(self.__seq_fr)
		offset_to = self.__calcOffset(self.__seq_to)
		
		if offset_fr > self.__idx_to:
			offset_fr = self.__idx_to
		if offset_to > self.__idx_to:
			offset_to = self.__idx_to
		
		return self.__readSequence(offset_fr, offset_to - offset_fr)
	
	def __getitem__(self, key):
		if isinstance(key, int):
			offset = self.__calcOffset(key)
			if offset < self.__idx_fr or offset >= self.__idx_to:
				raise IndexError('string index out of range')
			return self.__readSequence(offset, 1)
		elif isinstance(key, slice):
			fr = self.__seq_fr + key.start
			to = self.__seq_fr + key.stop
			
			if fr > self.__seq_to:
				fr = self.__seq_to
			if to > self.__seq_to:
				to = self.__seq_to
			
			seq = IndexedFastaSequence(self.__fname, self.__idx_fr, self.__idx_to,
			 self.__wrap, self.__newlines, fr, to)
			return seq
	
	def __iter__(self):
		# Jump to incorrect offset then correct for newlines.
		offset_fr = self.__calcOffset(self.__seq_fr)
		offset_to = self.__calcOffset(self.__seq_to)
		
		# Find the region between the two offsets
		infile = open(self.__fname)
		infile.seek(self.__idx_fr)
		infile.readline()
		infile.tell()
		infile.seek(offset_fr, 1)
		for i in xrange(offset_to - offset_fr):
			seq = infile.read(1)
			if len(seq.strip()) > 0:
				yield seq
		infile.close()
	
	def __calcOffset(self, pos):
		res = pos + (pos/self.__wrap) * len(self.__newlines)
		if pos%self.__wrap == 0:
			res -= len(self.__newlines)
		return res
	
	def __readSequence(self, fr, sz):
		infile = open(self.__fname)
		infile.seek(self.__idx_fr)
		infile.readline()
		infile.tell()
		infile.seek(fr, 1)
		seq = infile.read(sz)
		infile.close()
		return seq.replace(self.__newlines, '')

def getIndexName(fname):
	if '.' in fname:
		iname = fname[:fname.rfind('.')] + '.idx'
	else:
		iname = fname + '.idx'
	return iname

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

def iterFasta(fname):
	iname = getIndexName(fname)
	if os.path.exists(iname):
		return iterIndexedFasta(iname)
	return iterNormalFasta(fname)

def iterNormalFasta(fname):
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

def iterIndexedFasta(iname):
	import cPickle
	import stat
	
	# Get source file
	infile = open(iname, 'rb')
	mod = cPickle.load(infile)
	fname = cPickle.load(infile)
	if mod != os.stat(fname)[stat.ST_MTIME]:
		infile.close()
		raise SynchError
	wrap = cPickle.load(infile)
	newlines = cPickle.load(infile)
	idxs = cPickle.load(infile)
	end = cPickle.load(infile)
	infile.close()
	
	infile = open(fname)
	for i in xrange(len(idxs)):
		infile.seek(idxs[i])
		hdr = infile.readline()[1:].strip()
		idx_fr = idxs[i]
		idx_to = end
		if i < len(idxs) - 1:
			idx_to = idxs[i+1]
		
		seq = IndexedFastaSequence(fname, idx_fr, idx_to, wrap, newlines)
		yield (hdr, seq)
	infile.close()

def indxFasta(fname, iname = None):
	import cPickle
	import stat
	
	iname = getIndexName(fname)
	
	# Check to see if it already exists.
	if os.path.exists(iname):
		try:
			infile = open(iname, 'rb')
			iMod = cPickle.load(infile) # Indexed modification time.
			infile.close()
			
			cMod = os.stat(fname)[stat.ST_MTIME] # Current modification time.
			
			if iMod == cMod:
				return iname
		except EOFError, e: # If the file is empty then continue anyway.
			pass
	
	# Open the file handle
	infile = open(fname, 'rU')
	# Determine the wrap size
	wrap = 0
	for line in infile:
		if line[0] not in '#>':
			wrap = len(line.strip())
			break
	infile.seek(0)
	
	idxs = []
	lineno = 0
	wrap_err = None
	while True: # Equivalent of do-while loop.
		idx = infile.tell()
		line = infile.readline()
		
		if len(line) <= 0: # Exit condition
			break
		elif line[0] == '>':
			idxs.append(idx)
			wrap_err = None
		elif line[0] not in '#':
			if wrap_err:
				raise wrap_err
			elif len(line.strip()) != wrap:
				wrap_err = WrapError(lineno, wrap)
		lineno += 1
	newlines = infile.newlines
	end = infile.tell()
	infile.close()
	
	# Pickle the index to improve file access speed.
	outfile = file(iname, 'wb')
	cPickle.dump(os.stat(fname)[stat.ST_MTIME], outfile, cPickle.HIGHEST_PROTOCOL)
	cPickle.dump(fname, outfile, cPickle.HIGHEST_PROTOCOL)
	cPickle.dump(wrap, outfile, cPickle.HIGHEST_PROTOCOL)
	cPickle.dump(newlines, outfile, cPickle.HIGHEST_PROTOCOL)
	cPickle.dump(idxs, outfile, cPickle.HIGHEST_PROTOCOL)
	cPickle.dump(end, outfile, cPickle.HIGHEST_PROTOCOL)
	outfile.close()
	
	return iname

def split_file(infname, npart, outdname=None):
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

def flatten_file(infname):
	import shutil
	from tempfile import mkstemp
	
	outfile, outfname = mkstemp()
	os.close(outfile)
	writeFasta(iterFasta(infname), outfname)
	shutil.move(outfname, infname)

def main(argv = None):
	if argv == None:
		argv = sys.argv
	
	if argv[1] == 'index':
		index_file(argv[2])
	elif argv[1] == 'split':
		split_file(argv[2], int(argv[3]), '%s_%s'%(argv[2], argv[3]))
	elif argv[1] == 'flatten':
		flatten_file(argv[2])
	else:
		print 'Argument 1 must be either index or flatten'

if __name__ == '__main__':
	sys.exit(main(sys.argv))
