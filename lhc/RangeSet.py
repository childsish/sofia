#!/usr/bin/python

class RangeSet:
	def __init__(self, rngs):
		self.rngs = sorted(rngs)
	
	def getWithinRange(self, rng):
		return self.__getWithinRange(rng, 0, len(self.rngs))
	
	def getOverlappingRange(self, rng):
		return self.__getOverlappingRange(rng, 0, len(self.rngs))
	
	def getTouchingRange(self, rng):
		return self.__getTouchingRange(rng, 0, len(self.rngs))
	
	def __getWithinRange(self, rng, fr, to):
		if to - fr <= 1:
			res = []
			while self.__rngs[fr].f < rng.f:
				fr += 1
			to = fr
			while self.__rngs[fr].t < rng.t:
				to += 1
			return self.__rngs[fr:to]
		
		m = (fr + to) / 2
		if self.__rngs[m].f < rng.f:
			return self.__getWithinRange(rng, m, to)
		return self.__getWithinRange(rng, fr, m)

	def __getOverlappingRange(self, rng, fr, to):
		if to - fr <= 1:
			res = []
			while self.__rngs[fr].t < rng.f:
				fr += 1
			to = fr
			while self.__rngs[fr].f < rng.t:
				to += 1
			return self.__rngs[fr:to]
		
		m = (fr + to) / 2
		if self.__rngs[m].f < rng.f:
			return self.__getWithinRange(rng, m, to)
		return self.__getWithinRange(rng, fr, m)

	def __getTouchingRange(self, rng, fr, to):
		if to - fr <= 1:
			res = []
			while self.__rngs[fr].t <= rng.f:
				fr += 1
			to = fr
			while self.__rngs[fr].f <= rng.t:
				to += 1
			return self.__rngs[fr:to]
		
		m = (fr + to) / 2
		if self.__rngs[m].f < rng.f:
			return self.__getWithinRange(rng, m, to)
		return self.__getWithinRange(rng, fr, m)
