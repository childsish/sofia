import unittest

from lhc.binf.genomic_coordinate import GenomicInterval as Interval


class TestGenomicInterval(unittest.TestCase):
    def test_comparisons(self):
        a = Interval('1', 0, 10)
        b = Interval('1', 5, 10)
        c = Interval('1', 5, 15)
        d = Interval('2', 0, 10)

        self.assertTrue(a == a)
        self.assertFalse(a == b)
        self.assertFalse(b == a)
        
        self.assertTrue(a < b)
        self.assertFalse(b < a)
        self.assertTrue(b < c)
        self.assertFalse(c < b)
        
        self.assertFalse(a == d)
        self.assertFalse(d == a)

if __name__ == '__main__':
    unittest.main()
