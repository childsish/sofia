#!/usr/bin/python

class RangeSet:
	
	class Node:
		def __init__(self, f, t):
			
	
	def __init__(self, f, t):
		self.__f = f
		self.__t = t
	
	def query(self, rng):
		if rng.f < self.__f or rng.t > self.__t:
			raise IndexError('Range out of bounds.')
		
		
	
	def insert(self, rng):
		