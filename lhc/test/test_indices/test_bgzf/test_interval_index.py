__author__ = 'Liam Childs'

import unittest

from lhc.interval import Interval as I
from lhc.indices.bgzf.interval_index import IntervalIndex


class TestIntervalIndex(unittest.TestCase):
    def setUp(self):
        self.index = IntervalIndex()
        self.index.add([I(0, 25)], 0)
        self.index.add([I(0, 5)], 0)
        self.index.add([I(10, 15)], 1)
        self.index.add([I(20, 25)], 2)

    def test_contains(self):
        self.assertIn([I(5, 10)], self.index)
        self.assertNotIn([I(25, 30)], self.index)

    def test_fetch(self):
        self.assertEquals({0}, self.index.fetch(I(0, 5)))
        self.assertEquals({0, 2}, self.index.fetch(I(20, 25)))

    def test_fetch_extraarg(self):
        self.assertEquals({0}, self.index.fetch(0, 5))
        self.assertEquals({0, 2}, self.index.fetch(20, 25))

    def test_add_nonoverlapping_new_block(self):
        self.index.add([I(30, 35)], 3)

        self.assertEquals(2, len(self.index.tracks[0].starts))
        self.assertEquals(2, len(self.index.tracks[1].starts))

    def test_add_nonoverlapping_existing_block(self):
        self.index.add([I(30, 35)], 2)

        self.assertEquals(2, len(self.index.tracks[0].starts))
        self.assertEquals(2, len(self.index.tracks[1].starts))

    def test_add_overlapping_new_block(self):
        self.index.add([I(24, 35)], 3)

        self.assertEquals(1, len(self.index.tracks[0].starts))
        self.assertEquals(2, len(self.index.tracks[1].starts))

    def test_add_overlapping_existing_block(self):
        self.index.add([I(24, 35)], 2)

        self.assertEquals(1, len(self.index.tracks[0].starts))
        self.assertEquals(2, len(self.index.tracks[1].starts))


if __name__ == '__main__':
    unittest.main()
