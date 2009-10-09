from Vector import Vector

class Point:
	def __init__(self, x=0, y=0, z=0):
		self.x = x
		self.y = y
		self.z = z
	
	def __sub__(self, other):
		if isinstance(other, Point):
			return Vector(self.x - other.x, self.y - other.y, self.z - other.z)
		elif isinstance(other, Vector):
			return Point(self.x - other.x, self.y - other.y, self.z - other.z)
	
	def __add__(self, other):
		if not other.isinstance(Vector):
			raise Exception('Can only add Vectors to Points')
		
		return Point(self.x + other.x, self.y + other.y, self.z + other.z)
