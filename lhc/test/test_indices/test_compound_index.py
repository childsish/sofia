import cPickle
import os
import tempfile
import unittest

from lhc.interval import Interval

from lhc.indices.compound_index import CompoundIndex, KeyValuePair
from lhc.indices.key_index import KeyIndex
from lhc.indices.point_index import PointIndex
from lhc.indices.interval_index import IntervalIndex

class Test(unittest.TestCase):

    def testExactKey(self):
        index = CompoundIndex((KeyIndex,))
        index['a'] = 10
        index['a'] = 20
        
        self.assertEquals(index['a'], 20)
        self.assertRaises(KeyError, index.__getitem__, 'b')
    
    def testPointBelow(self):
        index = CompoundIndex((PointIndex,))
        index[10] = 'a'
        index[20] = 'b'
        
        self.assertEquals(index[9], None)
        self.assertEquals(index[10], (10, 'a'))
        self.assertEquals(index[19], (10, 'a'))
        self.assertEquals(index[20], (20, 'b'))
    
    def testOverlappingInterval(self):
        index = CompoundIndex((IntervalIndex,))
        index[Interval(1111190, 1111200)] = 'a'
        
        self.assertEquals(index[Interval(1111195, 1111205)], [(Interval(1111190, 1111200), 'a')])
    
    def testEKPB(self):
        index = CompoundIndex((KeyIndex, PointIndex))
        index[('x', 0)] = 'a'
        index[('x', 10)] = 'b'
        index[('x', 20)] = 'c'
        index[('y', 0)] = 'a'
        index[('y', 10)] = 'b'
        index[('y', 10)] = 'c'
        
        self.assertEquals(index[('x', 0)], KeyValuePair(('x', 0), 'a'))
        self.assertEquals(index[('x', 10)], KeyValuePair(('x', 10), 'b'))
        self.assertEquals(index[('x', 20)], KeyValuePair(('x', 20), 'c'))
        self.assertEquals(index[('x', 19)], KeyValuePair(('x', 10), 'b'))
        self.assertEquals(index[('x', 100)], KeyValuePair(('x', 20), 'c'))
        
        self.assertEquals(index[('y', 0)], KeyValuePair(('y', 0), 'a'))
        self.assertEquals(index[('y', 10)], KeyValuePair(('y', 10), 'c'))
    
    def testEKOI(self):
        index = CompoundIndex((KeyIndex, IntervalIndex))
        index[('chr1', Interval(1111190, 1111200))] = 'a'
        index[('chr2', Interval(1111190, 1111200))] = 'b'
        
        self.assertEquals(index[('chr1', Interval(1111195, 1111205))], [(('chr1', Interval(1111190, 1111200)), 'a')])
    
    def testEKEK(self):
        index = CompoundIndex((KeyIndex, KeyIndex))
        index[('chr1', 100)] = 'a'
        index[('chr1', 200)] = 'b'
        index[('chr1', 200)] = 'c'
        index[('chr2', 100)] = 'd'
        index[('chr2', 200)] = 'e'
        
        self.assertEquals(index[('chr1', 100)], 'a')
        self.assertEquals(index[('chr1', 200)], 'c')
        self.assertEquals(index[('chr2', 100)], 'd')
        self.assertEquals(index[('chr2', 200)], 'e')
    
    def test_pickleEKEK(self):
        index = CompoundIndex((KeyIndex, KeyIndex))
        index[('chr1', 100)] = 'a'
        index[('chr1', 200)] = 'b'

        fhndl, fname = tempfile.mkstemp()
        fhndl = os.fdopen(fhndl, 'w')
        cPickle.dump(index, fhndl)
        fhndl.close()

        infile = open(fname)
        index = cPickle.load(infile)
        self.assertEquals(index[('chr1', 100)], 'a')
        self.assertEquals(index[('chr1', 200)], 'b')
        infile.close()
        os.remove(fname)

if __name__ == "__main__":
    unittest.main()

