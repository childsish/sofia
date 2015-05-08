import unittest

from lhc.interval import Interval
from lhc.binf.genomic_coordinate import Interval as GenomicInterval
from lhc.indices.compound_index import CompoundIndex, KeyValuePair
from lhc.indices.key_index import KeyIndex
from lhc.indices.point_index import PointIndex
from lhc.indices.interval_index import IntervalIndex


class Test(unittest.TestCase):
    def testEKPB(self):
        index = CompoundIndex(KeyIndex, PointIndex)
        index[('x', 0)] = 'a'
        index[('x', 10)] = 'b'
        index[('x', 20)] = 'c'
        index[('y', 0)] = 'a'
        index[('y', 10)] = 'b'
        index[('y', 10)] = 'c'
        
        self.assertEquals(KeyValuePair(('x', 0), 'a'), index[('x', 0)])
        self.assertEquals(KeyValuePair(('x', 10), 'b'), index[('x', 10)])
        self.assertEquals(KeyValuePair(('x', 20), 'c'), index[('x', 20)])
        self.assertEquals(KeyValuePair(('x', 10), 'b'), index[('x', 19)])
        self.assertEquals(KeyValuePair(('x', 20), 'c'), index[('x', 100)])
        
        self.assertEquals(index[('y', 0)], KeyValuePair(('y', 0), 'a'))
        self.assertEquals(index[('y', 10)], KeyValuePair(('y', 10), 'c'))

    def testKIII(self):
        index = CompoundIndex(KeyIndex, IntervalIndex)
        index[('chr1', Interval(1111190, 1111200))] = 'a'
        index[('chr2', Interval(1111190, 1111200))] = 'b'

        res = index[('chr1', Interval(1111195, 1111205))]

        self.assertEquals(res[0].key, ('chr1', Interval(1111190, 1111200)))
        self.assertEquals(res[0].value, 'a')

    def testKIII_with_key(self):
        index = CompoundIndex(KeyIndex, IntervalIndex, key=lambda x: (x.chr, x))
        index[GenomicInterval('chr1', 1111190, 1111200)] = 'a'
        index[GenomicInterval('chr2', 1111190, 1111200)] = 'b'

        res = index[GenomicInterval('chr1', 1111195, 1111205)]

        self.assertEquals(res[0].key, GenomicInterval('chr1', 1111190, 1111200))
        self.assertEquals(res[0].value, 'a')
    
    def testEKEK(self):
        index = CompoundIndex(KeyIndex, KeyIndex)
        index[('chr1', 100)] = 'a'
        index[('chr1', 200)] = 'b'
        index[('chr1', 200)] = 'c'
        index[('chr2', 100)] = 'd'
        index[('chr2', 200)] = 'e'
        
        self.assertEquals(index[('chr1', 100)], 'a')
        self.assertEquals(index[('chr1', 200)], 'c')
        self.assertEquals(index[('chr2', 100)], 'd')
        self.assertEquals(index[('chr2', 200)], 'e')

if __name__ == "__main__":
    unittest.main()
