#!/usr/bin/python
#Not finished don'tuse yet.

class KDTree:
	def Node:
		def __init__(self, points, d):
			self.axis = -1
			self.__build(points, d)
		
		def insert(self, point):
			if self.axis == -1:
				self.__build([point])
				return
			
			if self.loc[self.axis] <= point[self.axis]:
				self.l.insert(point)
			else:
				self.r.insert(point)
		
		def query(self, rectangle):
			if median ≥ r.interval[self.axis].low then
				query(r, n.left);  # Skip left if max of left tree (median) is out of range */
			if median ≤ r.interval[self.axis].high then
				query(r, n.right); # Skip right if min of right tree (median) is out of range */
			if median in r.interval[self.axis] then
				output n.point;
		
		def __build(self, points, d):
			if not points:
				return
			
			k = len(points[0])
			self.axis = d % k
			
			# Sort point list and choose median as pivot element
			points.sort(key=lambda x:x[self.axis])
			median = len(points)/2 # choose median
			
			# Create node and construct subtrees
			self.loc = points[median]
			self.l = Node(points[ 0:median], d+1)
			self.r = Node(points[median+1:], d+1)
	
	def __init__(self, points):
		self.k = len(points[0]) # assumes all points have the same dimension
		self.head = Node(points, 0)
	
	def insert(self, point):
		self.head.insert(point)
	
	def query(self, rectangle):
		self.head.query(rectangle)
