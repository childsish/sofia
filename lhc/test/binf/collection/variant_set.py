import unittest

from lhc.binf.variant import Variant
from lhc.binf.genomic_coordinate import Interval
from lhc.binf.collection.variant_set import VariantSet

class Test(unittest.TestCase):
    def test_getBin(self):
        variant_set = VariantSet(':memory:')
        
        self.assertEquals(variant_set._getBin(Interval('chr1', 1234567890, 1234567891)), 301234567)
        self.assertEquals(variant_set._getBin(Interval('chr1', 1234567800, 1234567891)), 301234567)
        self.assertEquals(variant_set._getBin(Interval('chr1', 1234567000, 1234567891)), 301234567)
        self.assertEquals(variant_set._getBin(Interval('chr1', 1234560000, 1234567891)), 400123456)
        self.assertEquals(variant_set._getBin(Interval('chr1', 1234500000, 1234567891)), 500012345)
        self.assertEquals(variant_set._getBin(Interval('chr1', 1234000000, 1234567891)), 600001234)
        self.assertEquals(variant_set._getBin(Interval('chr1', 1230000000, 1234567891)), 700000123)
        self.assertEquals(variant_set._getBin(Interval('chr1', 1200000000, 1234567891)), 800000000)
        self.assertEquals(variant_set._getBin(Interval('chr1', 1000000000, 1234567891)), 800000000)
    
    def test_getOverlappingBins(self):
        variant_set = VariantSet(':memory:')
        
        self.assertEquals(variant_set._getOverlappingBins(Interval('chr1', 1234567890, 1234567891)),
            [(301234567, 301234567), (400123456, 400123456), (500012345, 500012345), (600001234, 600001234), (700000123, 700000123), (800000000, 800000000)])
        self.assertEquals(variant_set._getOverlappingBins(Interval('chr1', 1234567800, 1234567891)),
            [(301234567, 301234567), (400123456, 400123456), (500012345, 500012345), (600001234, 600001234), (700000123, 700000123), (800000000, 800000000)])
        self.assertEquals(variant_set._getOverlappingBins(Interval('chr1', 1234567000, 1234567891)),
            [(301234567, 301234567), (400123456, 400123456), (500012345, 500012345), (600001234, 600001234), (700000123, 700000123), (800000000, 800000000)])
        self.assertEquals(variant_set._getOverlappingBins(Interval('chr1', 1234560000, 1234567891)),
            [(301234560, 301234567), (400123456, 400123456), (500012345, 500012345), (600001234, 600001234), (700000123, 700000123), (800000000, 800000000)])
        self.assertEquals(variant_set._getOverlappingBins(Interval('chr1', 1234500000, 1234567891)),
            [(301234500, 301234567), (400123450, 400123456), (500012345, 500012345), (600001234, 600001234), (700000123, 700000123), (800000000, 800000000)])
        self.assertEquals(variant_set._getOverlappingBins(Interval('chr1', 1234000000, 1234567891)),
            [(301234000, 301234567), (400123400, 400123456), (500012340, 500012345), (600001234, 600001234), (700000123, 700000123), (800000000, 800000000)])
        self.assertEquals(variant_set._getOverlappingBins(Interval('chr1', 1230000000, 1234567891)),
            [(301230000, 301234567), (400123000, 400123456), (500012300, 500012345), (600001230, 600001234), (700000123, 700000123), (800000000, 800000000)])
        self.assertEquals(variant_set._getOverlappingBins(Interval('chr1', 1200000000, 1234567891)),
            [(301200000, 301234567), (400120000, 400123456), (500012000, 500012345), (600001200, 600001234), (700000120, 700000123), (800000000, 800000000)])
        self.assertEquals(variant_set._getOverlappingBins(Interval('chr1', 1000000000, 1234567891)),
            [(301000000, 301234567), (400100000, 400123456), (500010000, 500012345), (600001000, 600001234), (700000100, 700000123), (800000000, 800000000)])
    
    def test_overlap(self):
        ivls = [Variant(Interval('chr1', 1000010, 1000020), ['C']),
            Variant(Interval('chr1', 1000100, 1000200), ['A']),
            Variant(Interval('chr1', 1000500, 1000501), ['A']),
            Variant(Interval('chr1', 1000500, 1000501), ['C']),
            Variant(Interval('chr1', 1000500, 1000504), ['CTG'])
        ]
        variant_set = VariantSet(':memory:', ivls)
        
        self.assertEquals(variant_set.overlap(Interval('chr1', 1000000, 1001000)), ivls)
        self.assertEquals(variant_set.overlap(Interval('chr1', 1000000, 1000010)), [])
        self.assertEquals(variant_set.overlap(Interval('chr1', 1000020, 1000030)), [])
        
        self.assertEquals(variant_set.overlap(Interval('chr1', 1000050, 1000150)), ivls[1:2])
        self.assertEquals(variant_set.overlap(Interval('chr1', 1000150, 1000250)), ivls[1:2])
        self.assertEquals(variant_set.overlap(Interval('chr1', 1000050, 1000250)), ivls[1:2])
        self.assertEquals(variant_set.overlap(Interval('chr1', 1000140, 1000160)), ivls[1:2])
        
        self.assertEquals(set(map(str, variant_set.overlap(Interval('chr1', 1000500, 1000501)))), set(map(str, ivls[2:5])))

if __name__ == "__main__":
    unittest.main()
