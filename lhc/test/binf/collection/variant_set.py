import unittest

from lhc.binf.variant import Variant
from lhc.binf.genomic_coordinate import Interval
from lhc.binf.collection.variant_set import VariantSet

class Test(unittest.TestCase):
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
