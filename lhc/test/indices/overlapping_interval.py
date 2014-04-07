import unittest

from lhc.interval import Interval
from lhc.indices.overlapping_interval import OverlappingIntervalIndex

class TestOverlappingIntervalIndex(unittest.TestCase):
    
    def test_getitem(self):
        index = OverlappingIntervalIndex()
        index[Interval(10, 20)] = 'interval 1'
        index[Interval(30, 40)] = 'interval 2a'
        index[Interval(35, 45)] = 'interval 2b'
        index[Interval(55, 65)] = 'interval 3a'
        index[Interval(60, 70)] = 'interval 3b'
        index[Interval(80, 90)] = 'interval 4a'
        index[Interval(82, 88)] = 'interval 4b'
        index[Interval(102, 108)] = 'interval 5a'
        index[Interval(100, 110)] = 'interval 5b'
        
        self.assertEquals(index[Interval(0, 5)], [])
        self.assertEquals(index[Interval(5, 15)], ['interval 1'])
        self.assertEquals(index[Interval(10, 20)], ['interval 1'])
        self.assertEquals(index[Interval(15, 25)], ['interval 1'])
        self.assertEquals(index[Interval(10, 20)], ['interval 1'])
        self.assertEquals(index[Interval(5, 25)], ['interval 1'])
        self.assertEquals(index[Interval(12, 18)], ['interval 1'])
        self.assertEquals(index[Interval(22, 28)], [])
        
        self.assertEquals(index[Interval(30, 35)], ['interval 2a'])
        self.assertEquals(index[Interval(40, 45)], ['interval 2b'])
        self.assertEquals(index[Interval(30, 45)], ['interval 2a', 'interval 2b'])
        self.assertEquals(index[Interval(32, 43)], ['interval 2a', 'interval 2b'])
        
        self.assertEquals(index[Interval(55, 60)], ['interval 3a'])
        self.assertEquals(index[Interval(65, 70)], ['interval 3b'])
        self.assertEquals(index[Interval(55, 70)], ['interval 3a', 'interval 3b'])
        self.assertEquals(index[Interval(57, 68)], ['interval 3a', 'interval 3b'])

if __name__ == "__main__":
    unittest.main()
