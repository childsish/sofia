#--------------------------------------
# Systematically generate permutations. 
#--------------------------------------

import psyco
import numpy

from operator import mul

class PermutationGenerator:

	def __init__(self, n):
		if (n < 1):
			raise ValueError('n < 1')
		
		self.__a = numpy.zeros(n, dtype=numpy.int32)
		self.__total = self.__getFactorial(n)
		self.reset ()
	
	def __len__(self):
		return self.__total
	
	def __iter__(self):
		return self
	
	def reset(self):
		for i in xrange(len(self.__a)):
			self.__a[i] = i
		
		self.__numLeft = self.__total

	#------------------------------------------------
	# Return number of permutations not yet generated
	#------------------------------------------------

	def getNumLeft(self):
		self.__numLeft

	#-----------------------------
	# Are there more permutations?
	#-----------------------------

	def hasNext(self):
		return self.__numLeft > 0

	#------------------
	# Compute factorial
	#------------------

	def __getFactorial(self, n):
		return reduce(mul, range(2, n+1), 1)

	#--------------------------------------------------------
	# Generate next permutation (algorithm from Rosen p. 284)
	#--------------------------------------------------------

	def next(self):
		if self.__numLeft == 0:
			raise StopIteration()
		
		if self.__numLeft == self.__total:
			self.__numLeft -= 1
			return self.__a
	
		# Find largest index j with a[j] < a[j+1]
		j = len(self.__a) - 2
		while (self.__a[j] > self.__a[j+1]):
			j -= 1
		
		# Find index k such that a[k] is smallest integer
		# greater than a[j] to the right of a[j]
		k = len(self.__a) - 1
		while (self.__a[j] > self.__a[k]):
			k -= 1
	
		# Interchange a[j] and a[k]
		temp = self.__a[k]
		self.__a[k] = self.__a[j]
		self.__a[j] = temp
	
		# Put tail end of permutation after jth position in increasing order
		r = len(self.__a) - 1
		s = j + 1
	
		while (r > s):
			temp = self.__a[s]
			self.__a[s] = self.__a[r]
			self.__a[r] = temp
			r -= 1
			s += 1
		
		self.__numLeft -= 1
		return self.__a
psyco.bind(PermutationGenerator)

def main():
	tool = PermutationGenerator(4)
	for p in tool:
		print p
	
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main())
