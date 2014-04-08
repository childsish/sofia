import unittest

from lhc.interval import Interval

from lhc.indices.index import Index, KeyValuePair
from lhc.indices.exact_string import ExactStringIndex
from lhc.indices.point_below import PointBelowIndex
from lhc.indices.overlapping_interval import OverlappingIntervalIndex

class Test(unittest.TestCase):

    def testExactString(self):
        index = Index((ExactStringIndex,))
        index['a'] = 10
        index['a'] = 20
        
        self.assertEquals(index['a'], [('a', 20)])
    
    def testPointBelow(self):
        index = Index((PointBelowIndex,))
        index[10] = 'a'
        index[20] = 'b'
        
        self.assertEquals(index[9], [None])
        self.assertEquals(index[10], [(10, 'a')])
        self.assertEquals(index[19], [(10, 'a')])
        self.assertEquals(index[20], [(20, 'b')])
    
    def testOverlappingInterval(self):
        index = Index((OverlappingIntervalIndex,))
        index[Interval(1111190, 1111200)] = 'a'
        
        self.assertEquals(index[Interval(1111195, 1111205)], [(Interval(1111190, 1111200), 'a')])
    
    def testESandPB(self):
        index = Index((ExactStringIndex, PointBelowIndex))
        index[('x', 0)] = 'a'
        index[('x', 10)] = 'b'
        index[('x', 20)] = 'c'
        index[('y', 0)] = 'a'
        index[('y', 10)] = 'b'
        index[('y', 10)] = 'c'
        
        self.assertEquals(index[('x', 0)], [KeyValuePair(('x', 0), 'a')])
        self.assertEquals(index[('x', 10)], [KeyValuePair(('x', 10), 'b')])
        self.assertEquals(index[('x', 20)], [KeyValuePair(('x', 20), 'c')])
        self.assertEquals(index[('x', 19)], [KeyValuePair(('x', 10), 'b')])
        self.assertEquals(index[('x', 100)], [KeyValuePair(('x', 20), 'c')])
        
        self.assertEquals(index[('y', 0)], [KeyValuePair(('y', 0), 'a')])
        self.assertEquals(index[('y', 10)], [KeyValuePair(('y', 10), 'c')])
    
    def testESandOI(self):
        index = Index((ExactStringIndex, OverlappingIntervalIndex))
        index[('chr1', Interval(1111190, 1111200))] = 'a'
        index[('chr2', Interval(1111190, 1111200))] = 'b'
        
        self.assertEquals(index[('chr1', Interval(1111195, 1111205))], [(('chr1', Interval(1111190, 1111200)), 'a')])

if __name__ == "__main__":
    unittest.main()
