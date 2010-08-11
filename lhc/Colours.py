import numpy

class ColourDistribution:
	def __init__(self, breaks, r, g, b, a=None):
		self.__breaks = breaks
		self.__r = r
		self.__g = g
		self.__b = b
	
	def __call__(self, steps):
		return self.getDistribution(steps)
	
	def getDistribution(self, steps):
		res = numpy.zeros((steps, 4), dtype=numpy.float32)
		
		for i in xrange(steps):
			step = i/float(steps)
			
			c_break = self.__breaks * i / steps
			res[i,0] = (self.__breaks * step - c_break) *\
			 (self.__r[c_break][1] - self.__r[c_break][0]) +\
			 self.__r[c_break][0]
			res[i,1] = (self.__breaks * step - c_break) *\
			 (self.__g[c_break][1] - self.__g[c_break][0]) +\
			 self.__g[c_break][0]
			res[i,2] = (self.__breaks * step - c_break) *\
			 (self.__b[c_break][1] - self.__b[c_break][0]) +\
			 self.__b[c_break][0]
		
		return res

#class ColourClasses:
	#def __init__(self, cols):
		#self.__cols = numpy.array(cols, numpy.float32)
	
	#def getClasses(self, n):
		#return self.__cols[:n,:]

# Qualitative

def Rainbow(steps):
	r = [(1.0, 1.0), (1.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 1.0), (1.0, 1.0)]
	g = [(0.0, 1.0), (1.0, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0), (0.0, 0.0)]
	b = [(0.0, 0.0), (0.0, 0.0), (0.0, 1.0), (1.0, 1.0), (1.0, 1.0), (1.0, 0.0)]
	d = ColourDistribution(6, r, g, b)
	return d.getDistribution(steps)

# Look up http://www.personal.psu.edu/cab38/ColorBrewer/ColorBrewer.html
#def Pastels(steps):
	#cols = [(0.553, 0.827, 0.780), ()]
	#c = ColourClasses(cols)
	#return c.getClasses(steps)

# Quantitative

def YellowOrangeBrown(steps):
	r = numpy.array([[255, 255], [255, 254], [254, 254], [254, 254], [254, 236], [236, 204],
	 [204, 153], [153, 102]], dtype=numpy.float32)
	g = numpy.array([[255, 247], [247, 227], [227, 196], [196, 153], [153, 112], [112,  76],
	 [ 76,  52], [ 52,  37]], dtype=numpy.float32)
	b = numpy.array([[229, 188], [188, 145], [145,  79], [ 79,  41], [ 41,  20], [ 20,   2],
	 [  2,   4], [  4,   6]], dtype=numpy.float32)
	d = ColourDistribution(8, r/255, g/255, b/255)
	return d.getDistribution(steps)

# Diverging

def GreenMagenta(steps):
	r = [(0.0, 0.0), (0.3, 1.0), (1.0, 1.0), (1.0, 0.3)]
	g = [(0.3, 1.0), (1.0, 1.0), (1.0, 0.0), (0.0, 0.0)]
	d = ColourDistribution(4, r, g, r)
	return d.getDistribution(steps)

def BlueOrange(steps):
	r = [(0.0, 0.0), (0.0, 0.5), (0.5, 1.0), (1.0, 1.0), (1.0, 1.0), (1.0, 0.4)]
	g = [(0.4, 1.0), (1.0, 1.0), (1.0, 1.0), (1.0, 0.7), (0.7, 0.3), (0.3, 0.1)]
	b = [(0.4, 1.0), (1.0, 1.0), (1.0, 1.0), (1.0, 0.5), (0.5, 0.0), (0.0, 0.0)]
	d = ColourDistribution(6, r, g, b)
	return d.getDistribution(steps)

def BlueGreen(steps):
	r = [(0.0, 1.0), (1.0, 0.0)]
	g = [(0.0, 1.0), (1.0, 1.0)]
	b = [(1.0, 1.0), (1.0, 0.0)]
	d = ColourDistribution(2, r, g, b)
	return d.getDistribution(steps)

def toRString(col):
	c = col * 255
	return '#%02x%02x%02x'%(c[0], c[1], c[2])

def main():
	print Rainbow(8)
	print GreenMagenta(16)
	print BlueGreen(1000)
	print BlueOrange(50)
	yob = YellowOrangeBrown(50)
	for col in yob:
		print toRString(col), col
	return 0

if __name__ == '__main__':
	import sys
	sys.exit(main())

