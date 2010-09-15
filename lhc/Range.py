try:
	import psyco
	psyco.full()
except ImportError, e:
	import sys	
	sys.stderr.write('Unable to import psyco. Continuing without\n')

def extendAndReturn(x, y):
	x.extend(y)
	return x

class Range:
	def __init__(self, f, t):
		""" f must be smaller than t """
		self.f = min(f, t)
		self.t = max(f, t)
	
	def __len__(self):
		return self.t - self.f
	
	def __repr__(self):
		return '(%d,%d)'%(self.f, self.t)
	
	def __str__(self):
		return '(%d,%d)'%(self.f, self.t)
	
	def __lt__(self, other):
		return self.f < other.f
	
	def __le__(self, other):
		return self.f <= other.f
	
	def __eq__(self, other):
		if not isinstance(other, Range):
			return False
		return self.f == other.f and self.t == other.t
	
	def __ne__(self, other):
		if not isinstance(other, Range):
			return True
		return self.f != other.f or self.t != other.t
	
	def __gt__(self, other):
		return self.f > other.f
	
	def __ge__(self, other):
		return self.f >= other.f
	
	def __cmp__(self, other):
		return self.f - other.f
	
	def __hash__(self):
		return hash( (self.f, self.t) )
	
	def __sub__(self, other):
		if isinstance(other, SuperRange):
			return SuperRange([self]) - other
		elif self == other:
			return None #DELETED
		elif not self.overlaps(other):
			return self #NOEFFECT
		
		if self.f >= other.f:
			if self.t > other.t:
				return (None, Range(other.t, self.t)) #RIGHT
			return None #DELETED
		elif self.t > other.t:
			return (Range(self.f, other.f),Range(other.t, self.t)) #SPLIT
		return (Range(self.f, other.f), None) #LEFT
	
	def __and__(self, other):
		""" FIXME: Need to work for the case lots & one large. """
		if isinstance(other, SuperRange):
			return SuperRange([self]) & other
		elif self == other:
			return self
		elif not self.overlaps(other):
			return None
		
		if self.f >= other.f:
			if self.t > other.t:
				return Range(self.f, other.t)
			return self
		elif self.t >= other.t:
			return other
		return Range(other.f, self.t)
	
	def __or__(self, other):
		if isinstance(other, SuperRange):
			return SuperRange([self]) | other
		elif self == other:
			return self
		elif self.overlaps(other):
			return Range(min(self.f, other.f), max(self.t, other.t))
		return SuperRange([self, other])
	
	def toList(self):
		return [self]
	
	def overlaps(self, other):
		return (self.f <= other.f and self.t >= other.f) or\
		       (other.f <= self.f and other.t >= self.f)
	
	def contains(self, pos):
		return self.f <= pos and self.t > pos
	
	def getAbsPos(self, pos):
		""" Converts a position relative to the range to one relative to 0. """ 
		return pos + self.f
	
	def getRelPos(self, pos):
		""" Converts a position relative to 0 to one relative to the range. """
		return pos - self.f
	
	def getSubSeq(self, seq):
		return seq[self.f:self.t]
	
	def extend(self, value):
		if value < 0 and min(self.f, self.t) == self.f:
			self.f += value
		elif value < 0 and min(self.f, self.t) == self.t:
			self.t += value
		elif value >= 0 and min(self.f, self.t) == self.f:
			self.t += value
		elif value >= 0 and min(self.f, self.t) == self.t:
			self.f += value
	
	def shift(self, value):
		self.f += value
		self.t += value

class SuperRange:
	def __init__(self, rngs):
		self.__rngs = sorted(rngs)
		self.f = rngs[0].f
		self.t = rngs[-1].t
	
	def __len__(self):
		return sum([len(rng) for rng in self.__rngs])
	
	def __repr__(self):
		return '[%s]'%(', '.join([str(rng) for rng in self.__rngs]))
	
	def __str__(self):
		return '[%s]'%(', '.join([str(rng) for rng in self.__rngs]))
	
	def __lt__(self, other):
		return self.f < other.f
	
	def __le__(self, other):
		return self.f <= other.f
	
	def __eq__(self, other):
		if not isinstance(other, SuperRange):
			return False
		return self.f == other.f and self.t == other.t
	
	def __ne__(self, other):
		if not isinstance(other, SuperRange):
			return True
		return self.f != other.f or self.t != other.t
	
	def __gt__(self, other):
		return self.f > other.f
	
	def __ge__(self, other):
		return self.f >= other.f
	
	def __cmp__(self, other):
		return self.f - other.f
	
	def __iter__(self):
		return iter(self.__rngs)
	
	def __sub__(self, other):
		if isinstance(other, Range):
			other = SuperRange([other])
		
		iSelf = 0
		iOther = 0
		
		rngs = []
		while iSelf < len(self.__rngs) and iOther < len(other.__rngs):
			#print iSelf, ':', self.__rngs[iSelf]
			
			while iOther < len(other.__rngs) and\
			      other.__rngs[iOther].t <= self.__rngs[iSelf].f:
				iOther += 1
			
			pieces = (None, self.__rngs[iSelf])
			while iOther < len(other.__rngs) and\
			      pieces[1] != None and\
			      other.__rngs[iOther].f < pieces[1].t:
				#print pieces[1], '-', other.__rngs[iOther]
				pieces = pieces[1] - other.__rngs[iOther]
				if pieces == None:
					pieces = (None, None)
				if isinstance(pieces, Range):
					pieces = (pieces, None)
				if isinstance(pieces, SuperRange):
					pieces = pieces.toList()
					rngs += pieces[:-1]
					pieces = (None, pieces[-1])
				#print '=', pieces
				if pieces[0] != None: # If there is a left piece, append it.
					rngs.append(pieces[0])
				if pieces[1] != None:
					iOther += 1
			#print
			
			if pieces[1] != None:
				rngs.append(pieces[1])
			
			iSelf += 1
		
		if len(rngs) == 0:
			return None
		elif len(rngs) == 1:
			return rngs[0]
		return SuperRange(rngs)
	
	def __and__(self, other):
		if isinstance(other, Range):
			other = SuperRange([other])
		
		iSelf = 0
		iOther = 0
		
		rngs = []
		while iSelf < len(self.toList()) and iOther < len(other.toList()):
			#print iSelf
			while iOther < len(other.toList()) and\
			      other.toList()[iOther].f < self.toList()[iSelf].t:
				res = self.toList()[iSelf] & other.toList()[iOther]
				#print str(iOther) + str(self[iSelf]) + str(other[iOther]) + str(res)
				if res != None:
					rngs.append(res)
				iOther += 1
			#print
			iSelf += 1
		
		if len(rngs) == 0:
			return None
		elif len(rngs) == 1:
			return rngs[0]
		return SuperRange(rngs)
	
	def __or__(self, other):
		if isinstance(other, Range):
			other = SuperRange([other])
		
		allrngs = self.toList() + other.toList()
		rngs = [allrngs[0]]
		for i in xrange(1, len(allrngs)):
			if allrngs[i].overlaps(rngs[-1]):
				rngs[-1] = rngs[-1] | allrngs[i]
			else:
				rngs.append(allrngs[i])
		
		if len(rngs) == 0:
			return None
		elif len(rngs) == 1:
			return rngs[0]
		return SuperRange(rngs)
	
	def toList(self):
		return self.__rngs
	
	def overlaps(self, other):
		if isinstance(other, Range):
			other = SuperRange([other])
		
		for iSelf in xrange(len(self)):
			for iOther in xrange(len(other)):
				if self[iSelf].overlaps(other[iOther]):
					return True
		return False
	
	def contains(self, pos):
		for rng in self.__rngs:
			if rng.contains(pos):
				return True
		return False
	
	def getAbsPos(self, pos):
		""" Converts a position relative to the range to one relative to 0. """
		i = 0
		while i < len(self.__rngs) and len(self.__rngs[i]) <= pos:
			pos -= len(self.__rngs[i])
			i += 1
		
		if i == len(self.__rngs):
			raise IndexError('Relative position %d is not contained within this range'%pos)
		
		return self.__rngs[i].getAbsPos(pos)
	
	def getRelPos(self, pos):
		""" Converts a position relative to 0 to one relative to the range. """
		i = 0
		while i < len(self.__rngs):
			if self.__rngs[i].contains(pos):
				break
			i += 1
		
		if i == len(self.__rngs):
			raise IndexError('Absolute position %d is not contained within this range.'%pos)
		
		return sum([len(self.__rngs[j]) for j in xrange(i)]) + self.__rngs[i].getRelPos(pos)

	def getSubSeq(self, seq):
		res = []
		for rng in self.__rngs:
			res.append(rng.getSubSeq(seq))
		
		if isinstance(seq, basestring):
			res = ''.join(res)
		elif hasattr(seq, '__iter__'):
			res = reduce(extendAndReturn, res, []) # Flattens the list
			if isinstance(res[0], basestring):
				res = ''.join(res)
		
		return res
	
	def shift(self, offset):
		for rng in self.__rngs:
			rng.shift(offset)

def main():
	a = SuperRange([Range(3,  15), Range(40, 62)])
	b = SuperRange([Range(x*4+4, x*4+8) for x in xrange(0, 16, 2)])
	
	print a
	print b
	print b - a
	
	print a.getAbsPos(15)
	print a.getRelPos(43)

	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main())

