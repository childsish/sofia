from operator import add

class RangeError(Exception):
	pass

class Range(object):
	def __init__(self, f, t):
		""" f must be smaller than t """
		self.f = min(f, t)
		self.t = max(f, t)
	
	def __len__(self):
		if self.f > self.t:
			print self
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
		if self == NULL_RANGE:
			return NULL_RANGE
		elif other == NULL_RANGE:
			return self
		elif isinstance(other, SuperRange):
			return SuperRange([self]) - other
		elif self == other:
			return NULL_RANGE #DELETED
		elif not self.overlaps(other):
			return self #NOEFFECT
		
		if self.f >= other.f:
			if self.t > other.t:
				return Range(other.t, self.t) #RIGHT
			return NULL_RANGE #DELETED
		elif self.t > other.t:
			res = SuperRange([Range(self.f, other.f),
			 Range(other.t, self.t)]) #SPLIT
			return res
		return Range(self.f, other.f) #LEFT
	
	def __and__(self, other):
		if self == NULL_RANGE:
			return NULL_RANGE
		elif other == NULL_RANGE:
			return NULL_RANGE
		elif isinstance(other, SuperRange):
			return SuperRange([self]) & other
		elif self == other:
			return self
		elif not self.overlaps(other):
			return NULL_RANGE
		
		if self.f >= other.f:
			if self.t > other.t:
				return Range(self.f, other.t)
			return self
		elif self.t >= other.t:
			return other
		return Range(other.f, self.t)
	
	def __or__(self, other):
		if self == NULL_RANGE:
			return other
		elif other == NULL_RANGE:
			return self
		elif isinstance(other, SuperRange):
			return SuperRange([self]) | other
		elif self == other:
			return self
		elif self.overlaps(other) or self.adjacent(other):
			return Range(min(self.f, other.f), max(self.t, other.t))
		return SuperRange([self, other])
	
	def overlaps(self, other):
		return (self.f <= other.f and self.t > other.f) or\
		 (other.f <= self.f and other.t > self.f)
	
	def adjacent(self, other):
		return self.t == other.f or other.t == self.f
	
	def contains(self, pos):
		return self.f <= pos and self.t > pos
	
	def getAbsPos(self, pos):
		""" Converts a position relative to the range to one relative to 0. """
		return pos + self.f
	
	def getRelPos(self, pos):
		""" Converts a position relative to 0 to one relative to the range. """
		return pos - self.f
	
	def getSubSeq(self, seq):
		if self.f < 0:
			raise RangeError('Part of range not found in sequence: %d < 0'%\
			 self.f)
		elif self.t > len(seq):
			raise RangeError('Part of range not found in sequence: %d > %d'%\
			 (self.t, len(seq)))
		return seq[self.f:self.t]


class ImmutableRange(Range):
	def __init__(self, f, t):
		super(ImmutableRange, self).__setattr__('f', min(f, t))
		super(ImmutableRange, self).__setattr__('t', max(f, t))
	
	def __setattr__(self, key, value):
		""" Range is immutable. """
		raise TypeError('ImmutableRange is immutable.')
	__delattr__ = __setattr__

NULL_RANGE = ImmutableRange(0, 0)

class SuperRange(object):
	def __init__(self, rngs):
		self.__rngs = sorted(rngs)
		self.f = min((rng.f for rng in rngs))
		self.t = max((rng.t for rng in rngs))
	
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
		if self == NULL_RANGE:
			return NULL_RANGE
		elif other == NULL_RANGE:
			return self
		elif isinstance(other, Range):
			other = SuperRange([other])
		
		iS = 0
		iO = 0
		srngs = self.__rngs
		orngs = other.__rngs
		
		rngs = []
		while iS < len(srngs) and iO < len(orngs):
			while iO < len(orngs) and orngs[iO].t <= srngs[iS].f:
				iO += 1
			
			srng = srngs[iS]
			while srng != NULL_RANGE and iO < len(orngs) and orngs[iO].f < srng.t:
				orng = orngs[iO]
				srng = srng - orng
				if isinstance(srng, SuperRange):
					rngs.extend(srng.__rngs[:-1])
					srng = srng.__rngs[-1]
				elif isinstance(srng, Range):
					if srng.t <= orng.f:
						rngs.append(srng)
						srng = NULL_RANGE
					elif srng.f >= orng.t:
						iO += 1
			
			if srng != NULL_RANGE:
				rngs.append(srng)
			
			iS += 1
		
		if len(rngs) == 0:
			return NULL_RANGE
		elif len(rngs) == 1:
			return rngs[0]
		return SuperRange(rngs)
	
	def __and__(self, other):
		if other == NULL_RANGE:
			return NULL_RANGE
		elif isinstance(other, Range):
			other = SuperRange([other])
		
		iS = 0
		iO = 0
		srngs = self.__rngs
		orngs = other.__rngs
		
		rngs = []
		while iS < len(srngs) and iO < len(orngs):
			res = srngs[iS] & orngs[iO]
			if res != NULL_RANGE:
				rngs.append(res)
			
			diS = 0
			diO = 0
			if srngs[iS].t <= orngs[iO].t:
				diS = 1
			if orngs[iO].t <= srngs[iS].t:
				diO += 1
			
			iS += diS
			iO += diO
		
		if len(rngs) == 0:
			return NULL_RANGE
		elif len(rngs) == 1:
			return rngs[0]
		return SuperRange(rngs)
	
	def __or__(self, other):
		if other == NULL_RANGE:
			return self
		elif isinstance(other, Range):
			other = SuperRange([other])
		
		allrngs = self.toList() + other.toList()
		allrngs.sort()
		rngs = [allrngs[0]]
		for i in xrange(1, len(allrngs)):
			if allrngs[i].overlaps(rngs[-1]) or allrngs[i].adjacent(rngs[-1]):
				rngs[-1] = rngs[-1] | allrngs[i]
			else:
				rngs.append(allrngs[i])
		
		if len(rngs) == 0:
			return NULL_RANGE
		elif len(rngs) == 1:
			return rngs[0]
		return SuperRange(rngs)
	
	def setRanges(self, rngs):
		self.__rngs = sorted(rngs)
	
	def getRanges(self):
		return self.__rngs
	
	def overlaps(self, other):
		if isinstance(other, Range):
			other = SuperRange([other])
		
		for iS in xrange(len(self)):
			for iO in xrange(len(other)):
				if self[iS].overlaps(other[iO]):
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
		
		return self.__rngs[i].get_abs_pos(pos)
	
	def getRelPos(self, pos):
		""" Converts a position relative to 0 to one relative to the range. """
		i = 0
		while i < len(self.__rngs):
			if self.__rngs[i].contains(pos):
				break
			i += 1
		
		if i == len(self.__rngs):
			raise IndexError('Absolute position %d is not contained within this range.'%pos)
		
		return sum([len(self.__rngs[j]) for j in xrange(i)]) + self.__rngs[i].get_rel_pos(pos)

	def getSubSeq(self, seq):
		res = (rng.get_sub_seq(seq) for rng in self.__rngs)
		return reduce(add, res)
		
		#if isinstance(seq, basestring):
			#res = ''.join(res)
		#elif hasattr(seq, '__iter__'):
			#res = reduce(extendAndReturn, res, []) # Flattens the list
			#if isinstance(res[0], basestring):
				#res = ''.join(res)
		
		#return res

def _extendAndReturn(x, y):
	x.extend(y)
	return x

def main():
	a = Range(0, 10)
	b = Range(5, 15)
	assert(a & b == Range(5, 10))
	assert(b & a == Range(5, 10))
	assert(a | b == Range(0, 15))
	assert(b | a == Range(0, 15))
	assert(a - b == Range(0, 5))
	assert(b - a == Range(10, 15))
	
	a = Range(0, 1)
	b = Range(1, 2)
	print a & b == NULL_RANGE
	print b & a == NULL_RANGE
	print a | b == Range(0, 2)
	print b | a == Range(0, 2)
	print a - b == a
	print b - a == b
	print
	
	a = Range(0, 1)
	b = Range(2, 3)
	assert(a | b) == SuperRange([Range(0, 1), Range(2, 3)])
	
	a = SuperRange([Range(0, 1), Range(2, 3)])
	b = Range(1, 2)
	print a & b == NULL_RANGE
	print b & a == NULL_RANGE
	print a | b == Range(0, 3)
	print b | a == Range(0, 3)
	print a - b == a
	print b - a == b
	print
	
	a = SuperRange([Range(3,  15), Range(40, 62)])
	b = SuperRange([Range(x*4+4, x*4+8) for x in xrange(0, 16, 2)])
	print a & b == SuperRange([Range(4, 8), Range(12, 15), Range(44, 48), Range(52, 56), Range(60, 62)])
	print b & a == SuperRange([Range(4, 8), Range(12, 15), Range(44, 48), Range(52, 56), Range(60, 62)])
	print a | b == SuperRange([Range(3, 16), Range(20, 24), Range(28, 32), Range(36, 64)])
	print b | a == SuperRange([Range(3, 16), Range(20, 24), Range(28, 32), Range(36, 64)])
	print a - b == SuperRange([Range(3, 4), Range(8, 12), Range(40, 44), Range(48, 52), Range(56, 60)])
	print b - a == SuperRange([Range(15, 16), Range(20, 24), Range(28, 32), Range(36, 40), Range(62, 64)])
	print
	
	print a.getAbsPos(15) == 43
	print a.getRelPos(43) == 15
	
	a = SuperRange([Range(40,  62), Range(3, 15)])
	print a - b == SuperRange([Range(40, 44), Range(48, 52), Range(56, 60), Range(3, 4), Range(8, 12)])
	print
	
	a = SuperRange([SuperRange([Range(12, 16), Range(4, 8)]), Range(20, 30)])
	b = Range(13, 25)
	print a - b
	print b - a
	print a & b
	print b & a
	print a | b
	print b | a
	
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main())
