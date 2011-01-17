#--------------------------------------
# Systematically generate combinations.
#--------------------------------------

import numpy

from operator import mul

class CombinationGenerator:

	def __init__(self, n, r):
		self.__numLeft = 0
		
		if r > n:
			raise ValueError('r > n')
		if n < 1:
			raise ValueError('n < 1')
		
		self.__n = n
		self.__r = r
		self.__a = numpy.zeros(r, dtype=numpy.int32)
		
		nFact = self.__getFactorial(n)
		rFact = self.__getFactorial(r)
		nminusrFact = self.__getFactorial(n - r)
		self.__total = nFact / (rFact * nminusrFact)
		self.reset()

	def __len__(self):
		return self.__total
	
	def __iter__(self):
		return self

	def reset(self):
		self.__a = range(len(self.__a))
		self.__numLeft = self.__total

	#------------------------------------------------
	# Return number of combinations not yet generated
	#------------------------------------------------

	def getNumLeft(self):
		return self.__numLeft;

	#-----------------------------
	# Are there more combinations?
	#-----------------------------

	def hasNext(self):
		return self.__numLeft > 0

	#------------------
	# Compute factorial
	#------------------

	def __getFactorial(self, n):
		return reduce(mul, range(2, n+1), 1)

	#--------------------------------------------------------
	# Generate next combination (algorithm from Rosen p. 286)
	#--------------------------------------------------------

	def next(self):
		if self.__numLeft == 0:
			raise StopIteration()
		
		if self.__numLeft == self.__total:
			self.__numLeft -= 1
			return self.__a

		i = self.__r - 1
		while self.__a[i] == self.__n - self.__r + i:
			i -= 1
		self.__a[i] = self.__a[i] + 1;
		j = i + 1
		while j < self.__r:
			self.__a[j] = self.__a[i] + j - i
			j += 1
		
		self.__numLeft -= 1
		return self.__a
