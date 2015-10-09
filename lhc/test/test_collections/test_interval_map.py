__author__ = 'Liam Childs'

import unittest

from lhc.collections import IntervalMap
from lhc.interval import Interval


class TestIntervalMap(unittest.TestCase):
    def test_add(self):
        map_ = IntervalMap()

        map_[Interval(0, 1000)] = 1

        self.assertEquals(1, len(map_))
        self.assertTrue(any(Interval(0, 1000) in bin for bin in map_.bins.itervalues()))
        self.assertTrue(any(1 in value for value in map_.values.itervalues()))

    def test_init(self):
        map_ = IntervalMap([(Interval(0, 1000), 1), (Interval(1000, 2000), 2), (Interval(2000, 3000), 3)])

        self.assertEquals(3, len(map_))
        self.assertTrue(any(Interval(0, 1000) in bin for bin in map_.bins.itervalues()))
        self.assertTrue(any(1 in values for values in map_.values.itervalues()))
        self.assertTrue(any(Interval(1000, 2000) in bin for bin in map_.bins.itervalues()))
        self.assertTrue(any(2 in values for values in map_.values.itervalues()))
        self.assertTrue(any(Interval(2000, 3000) in bin for bin in map_.bins.itervalues()))
        self.assertTrue(any(3 in values for values in map_.values.itervalues()))

    def test_contains(self):
        map_ = IntervalMap([(Interval(0, 1000), 1), (Interval(1000, 2000), 2), (Interval(2000, 3000), 3)])

        self.assertIn(Interval(0, 1000), map_)
        self.assertIn(Interval(1000, 2000), map_)
        self.assertIn(Interval(2000, 3000), map_)

    def test_fetch(self):
        map_ = IntervalMap([(Interval(0, 1000), 1), (Interval(1000, 2000), 2), (Interval(2000, 3000), 3)])

        it = map_[Interval(500, 1500)]

        self.assertEquals(1, it.next())
        self.assertEquals(2, it.next())
        self.assertRaises(StopIteration, it.next)


if __name__ == '__main__':
    unittest.main()
