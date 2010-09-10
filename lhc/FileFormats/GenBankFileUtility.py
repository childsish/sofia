from Range import Range as BaseRange
from Range import SuperRange as BaseJoin
from sequence.seq_tools import rc

JOIN = 0
SPLIT = 1
IGNORE = 2

class TokeniserError(Exception):
	pass

class GenBankTokeniser:
	def tokenise(self, line):
		res = []
		fr = 0
		c_typ = self.__getTokenType(line[0])
		for to in xrange(len(line)-1):
			n_typ = self.__getTokenType(line[to+1])
			
			if c_typ[0] == JOIN and n_typ[1] != c_typ[1]:
				res.append(line[fr:to+1])
				fr = to+1
			elif c_typ[0] == SPLIT:
				res.append(line[fr:to+1])
				fr = to+1
			elif c_typ[0] == IGNORE:
				fr = to+1
			
			c_typ = n_typ
		res.append(line[fr:])
		return res
	
	def __getTokenType(self, char):
		""" Returns a 2-tuple (behaviour, type).
		 behaviours:
		  0 - join
		  1 - split
		  2 - ignore
		"""
		if char in '()':
			return (SPLIT,0)
		elif char == ',':
			return (SPLIT,1)
		elif char in '<>':
			return (IGNORE,2)
		elif char == '.':
			return (JOIN,3)
		elif char.isdigit():
			return (JOIN,4)
		elif char.isalpha():
			return (JOIN,5)
		elif char == '^':
			return (JOIN,6)
		elif char.isspace():
			return (IGNORE,7)
		else:
			raise TokeniserError('TokeniserException: "%s" can not be tokenised'%char)

def tokenise(line):
	tokeniser = GenBankTokeniser()
	return tokeniser.tokenise(line)

class Range(BaseRange):
	def __str__(self):
		return '%d..%d'%(self.f, self.t)
	
	def __sub__(self, other):
		""" Overridden so the Range types stay sequence friendly. """
		if isinstance(other, Complement):
			return self - other.getChild()
		elif isinstance(other, BaseJoin):
			res = BaseJoin([self]) - other
			return res
		elif self == other:
			return (None, None) #DELETED
		elif not self.overlaps(other):
			return self #NOEFFECT
		
		if self.f >= other.f:
			if self.t > other.t:
				return (None, Range(other.t, self.t)) #RIGHT
			return (None, None) #DELETED
		elif self.t > other.t:
			return (Range(self.f, other.f),Range(other.t, self.t)) #SPLIT
		return (Range(self.f, other.f), None) #LEFT
	
	def __and__(self, other):
		""" FIXME: Need to work for the case lots & one large. """
		if isinstance(other, Complement):
			return self & other.getChild()
		elif isinstance(other, Join):
			return Join([self]) & other
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
		if isinstance(other, Complement):
			return Join([self, other])
		return BaseRange.__or__(self, other)
	
	def isComplement(self):
		return False
	
	def get5p(self):
		return self.f
	
	def get3p(self):
		return self.t
	
	def set5p(self, val):
		self.f = val
	
	def set3p(self, val):
		self.t = val
	
	def adj5p(self, val):
		self.f += val
	
	def adj3p(self, val):
		self.t += val
	
	def getGenomic5p(self):
		return self.f
	
	def getGenomic3p(self):
		return self.t

class Complement(Range):
	def __init__(self, rng):
		Range.__init__(self, rng.f, rng.t)
		self.__rng = rng
	
	def __len__(self):
		return len(self.__rng)
	
	def __str__(self):
		return 'complement(%s)'%str(self.__rng)
	
	def __sub__(self, other):
		if isinstance(other, Complement):
			return Complement(self.__rng - other.__rng)
		res = self.__rng - other
		if res != None:
			res = Complement(res)
		return res
	
	def __and__(self, other):
		if isinstance(other, Complement):
			res = self.__rng & other.__rng
			if res != None:
				return Complement(res)
			else:
				return res
		elif isinstance(other, Range):
			res = self.__rng & other
			if res != None:
				return Complement(res)
			else:
				return res
		raise Exception('NotYetImplemented')
	
	def __or__(self, other):
		if isinstance(other, Range):
			return Join([self, other])
		elif isinstance(other, Complement):
			return Complement(self.rng | other.rng)
		raise Exception('NotYetImplemented')
	
	def isComplement(self):
		return True
	
	def getChild(self):
		return self.__rng
	
	def getAbsPos(self, pos):
		""" Converts a position relative to the range to one relative to 0. """ 
		return self.__rng.getAbsPos(len(self.__rng) - pos - 1)
	
	def getRelPos(self, pos):
		""" Converts a position relative to 0 to one relative to the range. """
		return len(self.__rng) - self.__rng.getRelPos(pos) - 1
	
	def getSubSeq(self, seq):
		return rc(str(self.__rng.getSubSeq(seq)))
	
	def get5p(self):
		return self.__rng.get3p()
	
	def get3p(self):
		return self.__rng.get5p()
	
	def set5p(self, val):
		self.__rng.set3p(val)
	
	def set3p(self, val):
		self.__rng.set5p(val)
	
	def adj5p(self, val):
		self.__rng.adj3p(-val)
	
	def adj3p(self, val):
		self.__rng.adj5p(-val)

class Join(BaseJoin):
	def __init__(self, rngs):
		BaseJoin.__init__(self, rngs)
		self.__rngs = rngs
	
	def __str__(self):
		return 'join(%s)'%','.join([str(rng) for rng in self.__rngs])
	
	def __sub__(self, other):
		return Join(BaseJoin.__sub__(self, other).toList())
	
	def isComplement(self):
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
		""" Overloaded to keep the order of ranges specified in the GenBankFile. """
		res = []
		for rng in self.__rngs:
			res.append(rng.getSubSeq(seq))
		
		res = ''.join(res)
		return res
	
	def get5p(self):
		return self.f
	
	def get3p(self):
		return self.t
	
	def set5p(self, val):
		self.__rngs[0].set5p(val)
		self.f = val
	
	def set3p(self, val):
		self.__rngs[-1].set3p(val)
		self.t = val
	
	def adj5p(self, val):
		self.__rngs[0].adj5p(val)
		self.f += val
	
	def adj3p(self, val):
		self.__rngs[-1].adj3p(val)
		self.t += val
	
	def getGenomic5p(self):
		return self.f
	
	def getGenomic3p(self):
		return self.t

def main():
	import random
	bases = 'actg'
	
	x1 = [0, 10]
	y1 = [5, 15]
	
	x2 = [10, 0]
	y2 = [15, 5]
	
	seq = ''.join([random.sample(bases, 1)[0] for i in xrange(20)])
	join1 = Join([Range(x1[i], y1[i]) for i in xrange(len(x1))])
	join2 = Join([Range(x2[i], y2[i]) for i in xrange(len(x1))])
	
	print seq
	print join1.getSubSeq(seq)
	print join2.getSubSeq(seq)

if __name__ == '__main__':
	import sys
	sys.exit(main())