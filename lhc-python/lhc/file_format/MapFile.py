#!/usr/bin/python

import psyco

psyco.full()

def readOne2Set(fname, k=lambda x:x[0], v=lambda x:x[1], delim='\t', skip_first=False):
	res = {}
	infile = open(fname)
	if skip_first:
		infile.readline()
	for line in infile:
		parts = line.strip().split(delim)
		res.setdefault(k(parts), set()).add(v(parts))
	infile.close()
	return res

def readOne2List(fname, k=lambda x:x[0], v=lambda x:x[1], delim='\t', skip_first=False):
	res = {}
	infile = open(fname)
	if skip_first:
		infile.readline()
	for line in infile:
		parts = line.strip().split(delim)
		res.setdefault(k(parts), []).append(v(parts))
	infile.close()
	return res

def readOne2One(fname, k=lambda x:x[0], v=lambda x:x[1], delim='\t', skip_first=False,\
 ignore=[]):
	res = {}
	infile = open(fname)
	if skip_first:
		infile.readline()
	for line in infile:
		parts = line.strip().split(delim)
		key = k(parts)
		if key in res:
			raise Exception('Key %s already exists'%(key))
		elif key in ignore:
			continue
		res[key] = v(parts)
	infile.close()
	return res
