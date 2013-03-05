#!/usr/bin/python

class Term:
	def __init__(self):
		self.p = None
		self.c = set()

class OboFile:
	def __init__(self, fname):
		self.ids = {}
		self.trms = {}
		
		infile = open(fname)
		for line in infile:
			pass
		infile.close()
