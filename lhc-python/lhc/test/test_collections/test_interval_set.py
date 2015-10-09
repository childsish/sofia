__author__ = 'Liam Childs'

import unittest

from lhc.collections import IntervalSet
from lhc.interval import Interval


class TestIntervalSet(unittest.TestCase):
    def test_add(self):
        set_ = IntervalSet()

        set_.add(Interval(0, 1000))

        self.assertEquals(1, len(set_))
        self.assertTrue(any(Interval(0, 1000) in bin for bin in set_.bins.itervalues()))

    def test_init(self):
        set_ = IntervalSet([Interval(0, 1000), Interval(1000, 2000), Interval(2000, 3000)])

        self.assertEquals(3, len(set_))
        self.assertTrue(any(Interval(0, 1000) in bin for bin in set_.bins.itervalues()))
        self.assertTrue(any(Interval(1000, 2000) in bin for bin in set_.bins.itervalues()))
        self.assertTrue(any(Interval(2000, 3000) in bin for bin in set_.bins.itervalues()))

    def test_contains(self):
        set_ = IntervalSet([Interval(0, 1000), Interval(1000, 2000), Interval(2000, 3000)])

        self.assertIn(Interval(0, 1000), set_)
        self.assertIn(Interval(1000, 2000), set_)
        self.assertIn(Interval(2000, 3000), set_)

    def test_fetch(self):
        set_ = IntervalSet([Interval(0, 1000), Interval(1000, 2000), Interval(2000, 3000)])

        it = set_.fetch(Interval(500, 1500))

        self.assertEquals(Interval(0, 1000), it.next())
        self.assertEquals(Interval(1000, 2000), it.next())
        self.assertRaises(StopIteration, it.next)


if __name__ == '__main__':
    unittest.main()
