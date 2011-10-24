import string

from binf.range import NULL_RANGE, Range as BaseRange, SuperRange as BaseJoin
from ushuffle import shuffle
from operator import add

def kshuffle(seq, k=2):
	return shuffle(seq, len(seq), k)

def revcmp(seq):
	m = string.maketrans('acgtuwrkysmbhdvnACGTUWRKYSMBHDVN', 'tgcaawymrskvdhbnTGCAAWYMRSKVDHBN')
	return seq.translate(m)[::-1]

class Range(BaseRange):
	def __init__(self, f, t):
		BaseRange.__init__(self, f, t)
	
	def __repr__(self):
		return '%d..%d'%(self.f, self.t)
	
	def __str__(self):
		return '%d..%d'%(self.f, self.t)
	
	def __sub__(self, other):
		if other.isComplement():
			other = other.rng
		
		if isinstance(other, Join):
			res = Join([self]) - other
			return res
		elif isinstance(other, Range):
			res = BaseRange.__sub__(self, other)
			if isinstance(res, BaseJoin):
				return Join([Range(rng.f, rng.t) for rng in res])
			elif isinstance(res, BaseRange):
				return Range(res.f, res.t)
			elif res is NULL_RANGE:
				return res
		
		raise NotImplementedError('')
	
	def __and__(self, other):
		if other.isComplement():
			other = other.rng
		
		if isinstance(other, Join):
			res = Join([self]) & other
			return res
		elif isinstance(other, Range):
			res = BaseRange.__and__(self, other)
			return Range(res.f, res.t)
		
		raise NotImplementedError('')
	
	def __or__(self, other):
		if self == NULL_RANGE:
			return other
		elif isinstance(other, Range):
			res = BaseRange.__or__(self, other)
			if isinstance(res, BaseJoin):
				return Join(res.getRanges())
			return Range(res.f, res.t)
		elif isinstance(other, Complement):
			return Join([self, other])
		elif isinstance(other, Join):
			return Join([self]) | other
		
		raise NotImplementedError('')
	
	def getSubSeq(self, seq, circular=False):
		if not circular:
			return BaseRange.getSubSeq(self, seq)
		
		res = []
		f = self.f
		if self.f < 0:
			rng = Range(len(seq) + self.f, len(seq))
			res.append(str(rng.getSubSeq(seq, circular)))
			f = 0
		res.append(str(seq[f:self.t]))
		if self.t > len(seq):
			rng = Range(0, self.t - len(seq))
			res.append(str(rng.getSubSeq(seq, circular)))
		
		return reduce(add, res)
	
	def isComplement(self):
		return False
	
	def get5p(self):
		return self.f
	
	def get3p(self):
		return self.t
	
	def set5p(self, val):
		self.f = val
		if self.f > self.t:
			self.t = self.f
	
	def set3p(self, val):
		self.t = val
		if self.t < self.f:
			self.f = self.t
	
	def adj5p(self, val):
		self.f += val
		if self.f > self.t:
			self.t = self.f
	
	def adj3p(self, val):
		self.t += val
		if self.t < self.f:
			self.f = self.t
	
	def getGenomic5p(self):
		return self.f
	
	def getGenomic3p(self):
		return self.t

class Complement(object):
	
	__REVCMPS = {basestring: revcmp, str: revcmp}
	
	def __init__(self, rng):
		self.rng = rng
		self.f = rng.f
		self.t = rng.t
	
	def __repr__(self):
		return 'complement(%s)'%str(self.rng)
	
	def __str__(self):
		return 'complement(%s)'%str(self.rng)
	
	def __len__(self):
		return len(self.rng)
	
	def __sub__(self, other):
		if other.isComplement():
			res = self.rng - other.rng
		else:
			res = self.rng - other
		
		if res != NULL_RANGE:
			res = Complement(res)
		return res
	
	def __and__(self, other):
		res = self.rng & other
		if res != NULL_RANGE:
			res = Complement(Range(res.f, res.t))
		return res
	
	def __or__(self, other):
		if self.rng == NULL_RANGE:
			return other
		elif isinstance(other, Range):
			return Join([self, other])
		elif isinstance(other, Complement):
			return Complement(self.rng | other.rng)
		elif isinstance(other, Join):
			return Join([self]) | other
		
		raise NotImplementedError('')
	
	def contains(self, pos):
		return self.rng.contains(pos)
	
	def isComplement(self):
		return True
	
	def getAbsPos(self, pos):
		""" Converts a position relative to the range to one relative to 0. """ 
		return self.rng.getAbsPos(len(self.rng) - pos - 1)
	
	def getRelPos(self, pos):
		""" Converts a position relative to 0 to one relative to the range. """
		return len(self.rng) - self.rng.getRelPos(pos) - 1
	
	def getSubSeq(self, seq, circular=False):
		return Complement.__REVCMPS[type(seq)](self.rng.getSubSeq(seq, circular))
	
	def get5p(self):
		return self.rng.get3p()
	
	def get3p(self):
		return self.rng.get5p()
	
	def set5p(self, val):
		self.rng.set3p(val)
	
	def set3p(self, val):
		self.rng.set5p(val)
	
	def adj5p(self, val):
		self.rng.adj3p(-val)
	
	def adj3p(self, val):
		self.rng.adj5p(-val)
	
	@classmethod
	def registerReverseComplement(cls, typ, fn):
		cls.__REVCMPS[typ] = fn

class Join(BaseJoin):
	""" Preserves order of sub ranges. """
	def __init__(self, rngs):
		BaseJoin.__init__(self, rngs)
		self.rngs = rngs
	
	def __str__(self):
		return 'join(%s)'%','.join([str(rng) for rng in self.rngs])
	
	def __sub__(self, other):
		if other.isComplement():
			other = other.rng
		
		res = BaseJoin.__sub__(self, other)
		if isinstance(res, BaseJoin):
			return Join(res.getRanges())
		return Range(res.f, res.t)
	
	def __or__(self, other):
		res = BaseJoin.__or__(self, other)
		if isinstance(res, BaseJoin):
			return Join(res.getRanges())
		return Range(res.f, res.t)
	
	def isComplement(self):
		return False
	
	def getAbsPos(self, pos):
		""" Converts a position relative to the range to one relative to 0. """
		i = 0
		while i < len(self.rngs) and len(self.rngs[i]) <= pos:
			pos -= len(self.rngs[i])
			i += 1
		
		if i == len(self.rngs):
			raise IndexError('Relative position %d is not contained within this range'%pos)
		
		return self.rngs[i].getAbsPos(pos)
	
	def getRelPos(self, pos):
		""" Converts a position relative to 0 to one relative to the range. """
		i = 0
		while i < len(self.rngs):
			if self.rngs[i].contains(pos):
				break
			i += 1
		
		if i == len(self.rngs):
			raise IndexError('Absolute position %d is not contained within this range.'%pos)
		
		return sum([len(self.rngs[j]) for j in xrange(i)]) + self.rngs[i].getRelPos(pos)
	
	def getSubSeq(self, seq, circular=False):
		""" Overloaded to keep the order of ranges specified in the GenBankFile. """
		res = (rng.getSubSeq(seq) for rng in self.rngs)
		return reduce(add, res)
	
	def get5p(self):
		return self.rngs[0].get5p()
	
	def get3p(self):
		return self.rngs[-1].get3p()
	
	def set5p(self, val):
		if self.contains(val):
			val = self.getRelPos(val)
			self.adj5p(val)
		else:
			self.rngs[0].set5p(val)
	
	def set3p(self, val):
		if self.contains(val):
			val = self.getRelPos(val) - len(self)
			self.adj3p(val)
		else:
			self.rngs[-1].set3p(val)
	
	def adj5p(self, val):
		"""Adjust the 5' position relative to the range. If adjustment moves 5' position
		 through a sub-range, the sub-range will be dropped."""
		if val <= 0:
			self.rngs[0].adj5p(val)
			return
		
		i = 0
		while i < len(self.rngs) and val - len(self.rngs[i]) > 0:
			val -= len(self.rngs[i])
			i += 1
		self.rngs[i].adj5p(val)
		self.rngs = self.rngs[i:]
		self.setRanges(self.rngs)
	
	def adj3p(self, val):
		if val >= 0:
			self.rngs[-1].adj3p(val)
		
		i = len(self.rngs) - 1
		while i >= 0 and val + len(self.rngs[i]) < 0:
			val += len(self.rngs[i])
			i -= 1
		self.rngs[i].adj3p(val)
		self.rngs = self.rngs[:i+1]
		self.setRanges(self.rngs)
	
	def getGenomic5p(self):
		return self.rngs[0].getGenomic5p()
	
	def getGenomic3p(self):
		return self.rngs[-1].getGenomic3p()

def main():
	a = Range(0, 10)
	b = Complement(Range(5, 15))
	print a & b == Range(5, 10)
	print b & a == Complement(5, 10)
	print a | b == Join([a, b])
	print b | a == Join([b, a])
	print a - b == Range(0, 5)
	print b - a == Complement(10, 15)
	print
	
	a = Range(0, 1)
	b = Complement(1, 2)
	print a & b == NULL_RANGE
	print b & a == NULL_RANGE
	print a | b == Join([a, b])
	print b | a == Join([b, a])
	print a - b == a
	print b - a == b
	print
	
	a = Join([Range(0, 1), Range(2, 3)])
	b = Range(1, 2)
	print a & b == NULL_RANGE
	print b & a == NULL_RANGE
	print a | b == Range(0, 3)
	print b | a == Range(0, 3)
	print a - b == a
	print b - a == b
	print
	
	a = Join([Range(3,  15), Range(40, 62)])
	b = Join([Range(x*4+4, x*4+8) for x in xrange(0, 16, 2)])
	print a & b == Join([Range(4, 8), Range(12, 15), Range(44, 48), Range(52, 56), Range(60, 62)])
	print b & a == Join([Range(4, 8), Range(12, 15), Range(44, 48), Range(52, 56), Range(60, 62)])
	print a | b == Join([Range(3, 16), Range(20, 24), Range(28, 32), Range(36, 64)])
	print b | a == Join([Range(3, 16), Range(20, 24), Range(28, 32), Range(36, 64)])
	print a - b == Join([Range(3, 4), Range(8, 12), Range(40, 44), Range(48, 52), Range(56, 60)])
	print b - a == Join([Range(15, 16), Range(20, 24), Range(28, 32), Range(36, 40), Range(62, 64)])
	print
	
	#print a.getAbsPos(15) == 43
	#print a.getRelPos(43) == 15
	
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main())
