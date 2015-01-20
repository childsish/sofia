import unittest

from lhc.binf.interval import Interval

class IntervalTest(unittest.TestCase):
	
	def test_getSubSeq_exactMatch1(self):
		seq = 'aaaaabbbbb'
		
		ivl = Interval(0, 10)
		self.assertEqual(ivl.getSubSeq(seq), 'aaaaabbbbb')
	
	def test_getSubSeq_exactMatch2(self):
		seq = 'aaaaabbbbb'
		
		ivl = Interval(0, 20)
		self.assertEqual(ivl.getSubSeq(seq), 'aaaaabbbbbaaaaabbbbb')
	
	def test_getSubSeq_offLeftEnd(self):
		seq = 'aaaaabbbbb'
		
		ivl = Interval(-8, -2)
		self.assertEqual(ivl.getSubSeq(seq), 'aaabbb')
	
	def test_getSubSeq_overlapLeftEnd(self):
		seq = 'aaaaabbbbb'
		
		ivl = Interval(-3, 3)		
		self.assertEqual(ivl.getSubSeq(seq), 'bbbaaa')
	
	def test_getSubSeq_offRightEnd(self):
		seq = 'aaaaabbbbb'
		
		ivl = Interval(12, 18)
		self.assertEqual(ivl.getSubSeq(seq), 'aaabbb')
	
	def test_getSubSeq_overlapRightEnd(self):
		seq = 'aaaaabbbbb'
		
		ivl = Interval(7, 13)		
		self.assertEqual(ivl.getSubSeq(seq), 'bbbaaa')
	
	def test_getSubSeq_inRange(self):
		seq = 'aaaaabbbbb'
		
		ivl = Interval(2, 8)
		self.assertEqual(ivl.getSubSeq(seq), 'aaabbb')
	
	def test_getSubSeq_multipleWrap(self):
		seq = 'aaaaabbbbb'
		
		ivl = Interval(-33, 33)
		self.assertEqual(ivl.getSubSeq(seq), 'bbbaaaaabbbbbaaaaabbbbbaaaaabbbbbaaaaabbbbbaaaaabbbbbaaaaabbbbbaaa')

if __name__ == '__main__':
	unittest.main()
