import itertools
import os
import paths
import re
import shutil
import subprocess
import tempfile

from paths import vienna

from FileFormats.ALNFile import ALNFile
def align(seqs):
	"""
	    Align sequences.
	    seqs: {acc: seq} OR
	    seqs: [seq]
	"""
	
	filename = None
	if isinstance(seqs, str):
		filename = seqs
	else:
		handle, filename = tempfile.mkstemp()
		
		if isinstance(seqs, dict):
			for acc, seq in seqs.iteritems(): os.write(handle, '>' + acc + '\n' + seq + '\n')
		elif isinstance(seqs, list):
			for i in xrange(len(seqs)): os.write(handle, '>' + str(i) + '\n' + seqs[i] + '\n')
		else:
			os.close(handle)
			raise TypeError('Expected filename, dict or list. Got ' + str(type(seqs)))
		
		os.close(handle)
	
	prc = subprocess.Popen([paths.align, '-INFILE=' + filename], stdout=subprocess.PIPE)
	stdout = prc.communicate()[0]
	
	basename = filename
	if '.' in filename:
		basename = filename[:filename.rfind('.')]
	aln = ALNFile(basename + '.aln')

	if not isinstance(seqs, str):
		os.remove(basename + '.dnd')
		os.remove(basename + '.aln')
		os.remove(filename)
	return aln

def alignNaByAa(na_seqs, gcode):
	aa_seqs = dict( ((key, gcode.translate(val)) for key, val in na_seqs.iteritems()))
	aa_alns = align(aa_seqs)
	
	na_alns = {}
	for key in na_seqs.iterkeys():
		na = na_seqs[key]
		aa = aa_alns[key]
		
		na_aln = aa_alns.getLength() * ['---']
		j = 0
		k = 0
		while j < len(aa):
			if aa[j] != '-':
				na_aln[j] = na[k:k+3]
				k += 3
			j += 1
		na_alns[key] = ''.join(na_aln)
	return na_alns

def blast(seq, database):
	handle, name = tempfile.mkstemp()
	os.write(handle, '>0\n' + seq + '\n')
	os.close(handle)
	
	prc = subprocess.Popen([paths.blastall,
	                        '-p', 'blastn',
	                        '-d', database,
	                        '-i', name,
	                        '-e', '1e-20',
	                        '-m', '8',
	                        '-W', '8',
	                        '-o', name + '.blast'])
	prc.wait()
	os.remove(name)
	
	infile = open(name + '.blast')
	res = infile.read()
	infile.close()
	os.remove(infile.name)
	
	return res

from operator import add
def countgc(seqs):
	res = len(seqs) * [None]
	for i in xrange(len(seqs)):
		res[i] = reduce(add, (c in 'GCgc' for c in seqs[i]) )
	return res

def dicodonshuffle(seq):
	seq.replace('-', '')
	handle, filename = tempfile.mkstemp()
	os.write(handle, 'ORIGIN\n' + seq + '\n')
	os.close(handle)
	
	prc = subprocess.Popen([paths.dicodonshuffle, filename, filename + '.out'],
	                       stdout=subprocess.PIPE,
	                       stderr=subprocess.PIPE)
	stdout, stderr = prc.communicate()
	os.remove(filename)
	
	infile = file(filename + '.out')
	infile.readline()
	out = ''.join([line.strip() for line in infile])
	out = out[:-2]
	infile.close()
	os.remove(infile.name)
	
	return out

def randfold(seqs):
	handle, filename = tempfile.mkstemp()
	for key, val in seqs.iteritems():
		os.write(handle, '>' + str(key) + '\n' + str(val) + '\n')
	os.close(handle)
	
	prc = subprocess.Popen([paths.misc.randfold, '-d', filename, '500'],
	                       stdout=subprocess.PIPE)
	res = {}
	for line in prc.stdout:
		if line == '':
			break
		parts = line.split()
		res[parts[0]] = (float(parts[1]), float(parts[2]), float(parts[3]))
	prc.wait()
	
	return res

def rnaeval(seqs, stcs): # sequences and structures. [[seq, str]]
	print 'Here'
	handle, filename = tempfile.mkstemp()
	for key in seqs:
		os.write(handle, '>' + key + '\n' + seqs[key] + '\n' + stcs[key] + '\n')
	os.close(handle)
	
	prc_in = open(filename)
	
	print prc_in.read()
	prc_in.seek(0)
	
	prc_out = open(filename + '.out', 'w')
	prc = subprocess.Popen([paths.rnaeval], stdin=prc_in, stdout=prc_out)
	prc.wait()
	prc_out.close()
	prc_in.close()
	
	infile = open(filename + '.out')
	print infile.read()
	infile.close()

def rnadist(s1, s2):
	filenames = []
	for k1, v1 in s1.iteritems():
		handle, filename = tempfile.mkstemp()
		
		os.write(handle, '>' + k1 + '\n' + v1 + '\n')
		for k2, v2 in s2.iteritems():
			os.write(handle, '>' + k2 + '\n' + v2 + '\n')
		os.close(handle)
		
		filenames.append(filename)
	
	res = {}
	
	for filename in filenames:
		prc_in = open(filename)
		prc_out = open(filename + '.out', 'w')
		prc = subprocess.Popen([paths.rnadist, '-Xf'], stdin=prc_in, stdout=prc_out)
		prc.wait()
		prc_out.close()
		prc_in.close()
		
		infile = open(filename + '.out')
		qry = infile.readline()[1:-1]
		line = infile.readline()
		while line != '':
			hit = line[1:-1]
			line = infile.readline()
			if line[0] != '>':
				scr = int(line[3:-1])
				res[(qry, hit)] = scr
				line = infile.readline()
		infile.close()
		
		os.remove(filename + '.out')
		os.remove(filename)
	
	return res

def rnasubopt(seq):
	handle, filename = tempfile.mkstemp()
	os.write(handle, seq)
	os.close(handle)
	
	prc_in = open(filename)
	prc_out = open(filename + '.out', 'w')
	prc = subprocess.Popen([paths.rnasubopt], stdin=prc_in, stdout=prc_out)
	prc.wait()
	prc_out.close()
	prc_in.close()
	
	infile = open(filename + '.out')
	infile.readline()
	infile.readline()
	lines = infile.readlines()
	infile.close()
	
	os.remove(filename + '.out')
	os.remove(filename)
	
	return lines

import random
from GeneticCode import GeneticCodes
gc = GeneticCodes(paths.misc.geneticcodes)
def alternative(seq, table = '1'):
	global gc
	code = gc[table]
	
	res = []
	
	i = 0
	while i < len(seq):
		codon = seq[i:i+3]
		if not codon in code:
			res.append(codon)
		else:
			try:
				aa = code[codon]
				alts = set(code[aa])
				if len(alts) > 1:
					alts -= set([codon])
				alt = random.choice(list(alts))
				res.append(alt)
			except ValueError, e:
				print e
				res.append(codon)
		i += 3
	return ''.join(res).lower()
