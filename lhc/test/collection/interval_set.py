import unittest

from lhc.interval import interval
from lhc.collection.interval_set import IntervalSet

class TestIntervalSet(unittest.TestCase):
    def test_getOverlap(self):
        a = IntervalSet([interval(0, 5), interval(10, 16), interval(20, 27)])
        b = IntervalSet([interval(0, 3), interval(6, 9), interval(12, 15), interval(18, 21), interval(24, 27), interval(30, 33)])
        
        c = a.getOverlap(b)
        for k, v in sorted(c.iteritems()):
            print k, map(str, v)


if __name__ == '__main__':
    unittest.main()
