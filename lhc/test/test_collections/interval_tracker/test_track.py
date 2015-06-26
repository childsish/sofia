__author__ = 'Liam Childs'

import unittest

from lhc.interval import Interval as I
from lhc.collections.interval_tracker import Track


class TestTrack(unittest.TestCase):
    def test_init(self):
        track = Track([I(0, 5, 0), I(10, 15, 1), I(20, 25, 2)])

        self.assertEquals([0, 10, 20], track.starts)
        self.assertEquals([5, 15, 25], track.stops)
        self.assertEquals([{0}, {1}, {2}], track.blocks)

    def test_insert(self):
        track = Track()
        track[I(0, 5)] = 0
        track[I(10, 15)] = 1
        track[I(20, 25)] = 2

        self.assertEquals([0, 10, 20], track.starts)
        self.assertEquals([5, 15, 25], track.stops)
        self.assertEquals([{0}, {1}, {2}], track.blocks)

    def test_contains(self):
        track = Track([I(0, 5, 0), I(10, 15, 1), I(20, 25, 2)])

        self.assertNotIn(I(-1, 0), track)
        self.assertIn(I(-1, 1), track)
        self.assertIn(I(1, 4), track)
        self.assertIn(I(4, 6), track)
        self.assertIn(I(-1, 6), track)
        self.assertNotIn(I(5, 6), track)

    def test_getitem(self):
        track = Track([I(0, 5, 0), I(10, 15, 1), I(20, 25, 2)])

        self.assertEquals({0, 1}, track[4:11])
        self.assertEquals(set(), track[5:10])
        self.assertEquals({1}, track[9:11])
        self.assertEquals({1}, track[14:16])
        self.assertEquals({1}, track[11:14])
        self.assertEquals({1}, track[9:16])
        self.assertEquals(set(), track[15:20])
        self.assertEquals({1, 2}, track[14:21])

    def test_setitem_nomerge(self):
        track = Track([I(0, 5, 0), I(10, 15, 1), I(20, 25, 2)])

        track[30:35] = 3

        self.assertEquals({2, 3}, track[24:31])
        self.assertEquals({3}, track[29:31])
        self.assertEquals({3}, track[34:36])

    def test_setitem_merge(self):
        track = Track([I(0, 5, 0), I(10, 15, 1), I(20, 25, 2)])

        track[14:21] = 3

        self.assertEquals({0}, track[4:6])
        self.assertEquals(set(), track[5:10])
        self.assertEquals({1, 2, 3}, track[9:11])
        self.assertEquals({1, 2, 3}, track[24:26])
        self.assertEquals({1, 2, 3}, track[15:20])

    def test_get_cost(self):
        track = Track([I(0, 5, 0), I(10, 15, 1), I(20, 25, 2)])

        self.assertEquals(1, track.get_cost())

    def test_get_cost_merge(self):
        track = Track([I(0, 5, 0), I(10, 15, 1), I(20, 25, 2)])

        track[14:21] = 2

        self.assertEquals(2, track.get_cost())

    def test_get_cost_merge_new(self):
        track = Track([I(0, 5, 0), I(10, 15, 1), I(20, 25, 2)])

        track[14:21] = 3

        self.assertEquals(3, track.get_cost())

    def test_get_cost_nochange(self):
        track = Track([I(0, 5, 0), I(10, 15, 1), I(20, 25, 2)])

        self.assertEquals(1, track.get_cost(I(30, 35), 3))
        self.assertEquals(3, track.get_cost(I(14, 21), 3))
        self.assertEquals(2, track.get_cost(I(14, 21), 2))
        self.assertRaises(ValueError, track.get_cost, I(14, 21))

    def test_intersect(self):
        track = Track([I(0, 5, 0), I(10, 15, 1), I(20, 25, 2)])

        self.assertEquals((0, 0), track._intersect(I(0, 0)))
        self.assertEquals((0, 1), track._intersect(I(0, 1)))
        self.assertEquals((0, 1), track._intersect(I(0, 10)))
        self.assertEquals((0, 2), track._intersect(I(0, 11)))
        self.assertEquals((0, 2), track._intersect(I(0, 20)))
        self.assertEquals((0, 3), track._intersect(I(0, 21)))
        self.assertEquals((0, 3), track._intersect(I(4, 21)))
        self.assertEquals((1, 3), track._intersect(I(5, 21)))
        self.assertEquals((1, 3), track._intersect(I(14, 21)))
        self.assertEquals((2, 3), track._intersect(I(15, 21)))
        self.assertEquals((2, 3), track._intersect(I(24, 25)))
        self.assertEquals((3, 3), track._intersect(I(25, 25)))

if __name__ == '__main__':
    unittest.main()
