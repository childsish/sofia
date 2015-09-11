__author__ = 'Liam Childs'

import unittest

from lhc.interval import Interval as I
from lhc.indices.bgzf.track import Track


class TestTrack(unittest.TestCase):
    def setUp(self):
        self.track = Track()
        self.track.add([I(0, 5)], 0)
        self.track.add([I(10, 15)], 1)
        self.track.add([I(20, 25)], 2)
        self.track.add([I(30, 35)], 2)

    def test_add(self):
        self.assertEquals([0, 10, 20, 30], self.track.starts)
        self.assertEquals([5, 15, 25, 35], self.track.stops)
        self.assertEquals([{0}, {1}, {2}, {2}], self.track.values)

    def test_contains(self):
        self.assertNotIn([I(-1, 0)], self.track)
        self.assertIn([I(-1, 1)], self.track)
        self.assertIn([I(1, 4)], self.track)
        self.assertIn([I(4, 6)], self.track)
        self.assertIn([I(-1, 6)], self.track)
        self.assertNotIn([I(5, 6)], self.track)

    def test_fetch(self):
        self.assertEquals({0, 1}, self.track.fetch(I(4, 11)))
        self.assertEquals(set(), self.track.fetch(I(5, 10)))
        self.assertEquals({1}, self.track.fetch(I(9, 11)))
        self.assertEquals({1}, self.track.fetch(I(14, 16)))
        self.assertEquals({1}, self.track.fetch(I(11, 14)))
        self.assertEquals({1}, self.track.fetch(I(9, 16)))
        self.assertEquals(set(), self.track.fetch(I(15, 20)))
        self.assertEquals({1, 2}, self.track.fetch(I(14, 21)))

    def test_fetch_extrarg(self):
        self.assertEquals({0, 1}, self.track.fetch(4, 11))
        self.assertEquals(set(), self.track.fetch(5, 10))
        self.assertEquals({1}, self.track.fetch(9, 11))
        self.assertEquals({1}, self.track.fetch(14, 16))
        self.assertEquals({1}, self.track.fetch(11, 14))
        self.assertEquals({1}, self.track.fetch(9, 16))
        self.assertEquals(set(), self.track.fetch(15, 20))
        self.assertEquals({1, 2}, self.track.fetch(14, 21))

    def test_add_nomerge(self):
        self.track.add([I(30, 35)], 3)

        self.assertEquals({2, 3}, self.track.fetch(24, 31))
        self.assertEquals({2, 3}, self.track.fetch(29, 31))
        self.assertEquals({2, 3}, self.track.fetch(34, 36))

    def test_add_merge(self):
        self.track.add([I(14, 21)], 3)

        self.assertEquals({0}, self.track.fetch(4, 6))
        self.assertEquals(set(), self.track.fetch(5, 10))
        self.assertEquals({1, 2, 3}, self.track.fetch(9, 11))
        self.assertEquals({1, 2, 3}, self.track.fetch(24, 26))
        self.assertEquals({1, 2, 3}, self.track.fetch(15, 20))

    def test_get_cost(self):
        self.assertEquals(1, self.track.get_cost())

    def test_get_cost_merge(self):
        self.track.add([I(14, 21)], 2)

        self.assertEquals(2, self.track.get_cost())

    def test_get_cost_merge_new(self):
        self.track.add([I(14, 21)], 3)

        self.assertEquals(3, self.track.get_cost())

    def test_get_cost_nochange(self):
        self.assertEquals(2, self.track.get_cost([I(30, 35)], 3))
        self.assertEquals(3, self.track.get_cost([I(14, 21)], 3))
        self.assertEquals(2, self.track.get_cost([I(14, 21)], 2))
        self.assertRaises(ValueError, self.track.get_cost, I(14, 21))

    def test_get_interval(self):
        self.assertEquals((0, 0), self.track._get_interval(0, 0))
        self.assertEquals((0, 1), self.track._get_interval(0, 1))
        self.assertEquals((0, 1), self.track._get_interval(0, 10))
        self.assertEquals((0, 2), self.track._get_interval(0, 11))
        self.assertEquals((0, 2), self.track._get_interval(0, 20))
        self.assertEquals((0, 3), self.track._get_interval(0, 21))
        self.assertEquals((0, 3), self.track._get_interval(4, 21))
        self.assertEquals((1, 3), self.track._get_interval(5, 21))
        self.assertEquals((1, 3), self.track._get_interval(14, 21))
        self.assertEquals((2, 3), self.track._get_interval(15, 21))
        self.assertEquals((2, 3), self.track._get_interval(24, 25))
        self.assertEquals((3, 3), self.track._get_interval(25, 25))

    def test_compress(self):
        track = self.track.compress()

        self.assertEquals([0, 10, 20], track.starts)
        self.assertEquals([5, 15, 35], track.stops)
        self.assertEquals([{0}, {1}, {2}], track.values)

    def test_compress_factor(self):
        track = self.track.compress(factor=2)

        self.assertEquals([0, 20], track.starts)
        self.assertEquals([15, 35], track.stops)
        self.assertEquals([{0, 1}, {2}], track.values)

if __name__ == '__main__':
    unittest.main()
