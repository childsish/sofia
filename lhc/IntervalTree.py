from Range import Range
from sys import maxint

try:
	import psyco
	psyco.full()
except ImportError:
	print 'Unable to import psyco'

class RecursionNode:
	def __init__(self, node, p_idx, try_r):
		self.node = node
		self.p_idx = p_idx
		self.try_r = try_r

class IterationNode:
	def __init__(self, node):
		self.node = node
		self.try_l = True

class Node:
	def __init__(self, rng):
		self.rng = rng
		self.mx = rng.t

		# Red/Black tree data
		self.red = False

		# Related nodes.
		self.l = None
		self.r = None
		self.p = None

	def __str__(self):
		res = str(self.rng)
		res += ', f=%i, t=%i, m=%i'%(self.rng.f, self.rng.t, self.mx)
		return res

	def toString(self, nil, head):
		res = str(self.rng)
		res += ', f=%i, t=%i, m=%i'%(self.rng.f, self.rng.t, self.mx)
		res += '  l.rng.f='
		if self.l == nil: res += 'NULL'
		else:             res += '%i'%(self.l.rng.f)
		res += '  r.rng.f='
		if self.r == nil: res += 'NULL'
		else:             res += '%i'%(self.r.rng.f)
		res += '  p.rng.f='
		if self.p == head: res += 'NULL'
		else:              res += '%i'%(self.p.rng.f)
		res += '  red=%i\n'%(self.red)
		return res

class IntervalTree:
	class Iterator:
		def __init__(self, tree):
			self.tree = tree
			iternode = IterationNode(self.tree.head.l)
			iternode.try_l = iternode.node.l != self.tree.nil
			self.stack = [iternode]
			self.count = 0
		
		def __iter__(self):
			return self
		
		def next(self):
			# Check if iteration stops.
			if len(self.stack) == 0:
				raise StopIteration
			
			# Push the left branches onto stack.
			while self.stack[-1].try_l:
				self.stack[-1].try_l = False
				iternode = IterationNode(self.stack[-1].node.l)
				iternode.try_l = iternode.node.l != self.tree.nil
				self.stack.append(iternode)
			
			res = self.stack.pop()
			if res.node.r != self.tree.nil:
				iternode = IterationNode(res.node.r)
				iternode.try_l = iternode.node.l != self.tree.nil
				self.stack.append(iternode)
			return res.node.rng
	
	def __init__(self, rngs=None):
		# Initialise sentinels
		self.nil = Node(Range(-maxint-1, -maxint-1))
		self.nil.l = self.nil
		self.nil.r = self.nil
		self.nil.p = self.nil
		
		self.head = Node(Range(maxint, maxint))
		self.head.l = self.nil
		self.head.r = self.nil
		self.head.p = self.nil
		
		if rngs != None:
			for rng in rngs:
				self.insert(rng)
	
	def __str__(self):
		return self.__treePrintHelper(self.head.l)
	
	def __iter__(self):
		return IntervalTree.Iterator(self)

	def insert(self, rng):
		x = Node(rng)
		self.__treeInsertHelp(x)
		self.__fixUpMaxHigh(x.p)
		newNode = x
		x.red = True
		while x.p.red: # use sentinel instead of checking for root
			if x.p == x.p.p.l:
				y = x.p.p.r
				if (y.red):
					x.p.red = False
					y.red = False
					x.p.p.red = True
					x = x.p.p
				else:
					if x == x.p.r:
						x = x.p
						self.__lRotate(x)
					x.p.red = False
					x.p.p.red = True
					self.__rRotate(x.p.p)
			else: # case for x.p == x.p.p.r
			      # this part is just like the section above with
			      # l and r interchanged
				y = x.p.p.l
				if y.red:
					x.p.red = False
					y.red = False
					x.p.p.red = True
					x = x.p.p
				else:
					if x == x.p.l:
						x = x.p
						self.__rRotate(x)
					x.p.red = False
					x.p.p.red = True
					self.__lRotate(x.p.p)
		self.head.l.red = False
		return newNode
	
	def getRange(self):
		x = self.head.l
		y = x
		while x != self.nil:
			y = x
			x = x.l
		return Range(y.rng.f, self.head.l.mx)
	
	def search(self, rng):
		""" Possible speed up: add min field to prune r searches. """
		x = self.head.l
		stuffToDo = x != self.nil
		
		c_parent = 0
		stack = [RecursionNode(None, c_parent, False)]
		
		res = []
		while(stuffToDo):
			if rng.overlaps(x.rng):
				res.append(x.rng)
				stack[c_parent].try_r = True
			
			if x.l.mx >= rng.f: # Implies x != nil 
				stack.append(RecursionNode(x, c_parent, False))
				c_parent = len(stack)-1
				x = x.l
			else:
				x = x.r
			
			stuffToDo = x != self.nil
			while (not stuffToDo) and (len(stack) > 1):
				rnode = stack.pop(-1)
				if rnode.try_r:
					x = rnode.node.r
					c_parent = rnode.p_idx
					stack[c_parent].try_r = True
					stuffToDo = x != self.nil
		return res
	
	def toFile(self, filename):
		import cPickle
		outfile = open(filename, 'w')
		cPickle.dump(self.head.l, outfile, cPickle.HIGHEST_PROTOCOL)
		outfile.close()
	
	def fromFile(self, filename):
		import cPickle
		infile = open(filename)
		self.head.l = cPickle.load(infile)
		infile.close()
	
	def __lRotate(self, x):
		y = x.r
		x.r = y.l

		if y.l != self.nil:
			y.l.p = x 

		y.p = x.p

		# Instead of checking if x.p is the root as in the book, we
		# count on the root sentinel to implicitly take care of this case
		if x == x.p.l:
			x.p.l = y
		else:
			x.p.r = y
		y.l = x
		x.p = y

		x.mx = max(x.l.mx, x.r.mx, x.rng.t)
		y.mx = max(x.mx, y.r.mx, y.rng.t)
	
	def __rRotate(self, y):
		x = y.l
		y.l = x.r

		# Used to use sentinel here and do an unconditional assignment instead of
		# testing for nil
		if self.nil != x.r:
			x.r.p=y

		# Instead of checking if x.p is the root as in the book, we
		# count on the root sentinel to implicitly take care of this case
		x.p = y.p
		if y == y.p.l:
			y.p.l = x
		else:
			y.p.r = x
		x.r = y
		y.p = x

		y.mx = max(y.l.mx, y.r.mx, y.rng.t)
		x.mx = max(x.l.mx, y.mx, x.rng.t)
	
	def __treeInsertHelp(self, z):
		z.l = self.nil
		z.r = self.nil
		y = self.head
		x = self.head.l
		while(x != self.nil):
			y = x
			if x.rng.f > z.rng.f:
				x = x.l
			else: # x.rng.f <= z.rng.f 
				x = x.r
		
		z.p = y
		if (y == self.head) or (y.rng.f > z.rng.f):
			y.l = z
		else:
			y.r = z

	def __fixUpMaxHigh(self, x):
		while x != self.head:
			x.mx = max(x.rng.t, x.l.mx, x.r.mx)
			x = x.p
	
	def __treePrintHelper(self, x):
		res = ''
		if (x != self.nil):
			res += self.__treePrintHelper(x.l)
			res += x.toString(self.nil, self.head)
			res += self.__treePrintHelper(x.r)
		return res

def main():
	import random
	
	rngs = []
	tree = IntervalTree()
	for i in xrange(15):
		l = random.randint(0, 100)
		r = random.randint(0, 100)
		rng = Range(min(l, r), max(l, r))
		rngs.append(rng)
		tree.insert(rng)
		print str(tree)
		print
	
	print tree.getRange()

	return 0

	for rng in rngs:
		print str(rng)
	print
	
	print str(tree)
	
	rng = Range(30, 30)
	print '*' + str(rng)
	res = tree.search(rng)
	for r in res:
		print r
		
	for node in tree:
		print node
	
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main())
