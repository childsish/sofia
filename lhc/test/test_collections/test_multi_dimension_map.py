__author__ = 'Liam Childs'

import unittest

from lhc.collections import MultiDimensionMap, IntervalMap
from lhc.interval import Interval


class TestMultiDimensionMap(unittest.TestCase):
    def test_add(self):
        map_ = MultiDimensionMap([str, Interval])

        map_[['Chr1', Interval(0, 1000)]] = 1

        self.assertEquals(1, len(map_))
        self.assertFalse(map_.root.is_last)
        self.assertIs(type(map_.root.map), dict)
        self.assertIs(type(map_.root.map['Chr1'].map), IntervalMap)
        self.assertIn(Interval(0, 1000), map_.root.map['Chr1'].map.bins.values()[0])
        self.assertIn(1, map_.root.map['Chr1'].map.values.values()[0])

    def test_init(self):
        map_ = MultiDimensionMap([str, Interval], [(('Chr1', Interval(1000, 2000)), 1),
                                                   (('Chr1', Interval(3000, 4000)), 2),
                                                   (('Chr2', Interval(1000, 2000)), 3),
                                                   (('Chr2', Interval(3000, 4000)), 4)])

        self.assertEquals(4, len(map_))
        self.assertEquals({'Chr1', 'Chr2'}, set(map_.root.map))

    def test_fetch(self):
        map_ = MultiDimensionMap([str, Interval], [(('Chr1', Interval(1000, 2000)), 1),
                                                   (('Chr1', Interval(3000, 4000)), 2),
                                                   (('Chr2', Interval(1000, 2000)), 3),
                                                   (('Chr2', Interval(3000, 4000)), 4)])

        it = map_[('Chr2', Interval(1500, 3500))]

        self.assertEquals(3, it.next())
        self.assertEquals(4, it.next())
        self.assertRaises(StopIteration, it.next)


if __name__ == '__main__':
    unittest.main()
