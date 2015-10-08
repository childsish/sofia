__author__ = 'Liam Childs'

import unittest

from Bio import bgzf
from lhc.interval import Interval
from lhc.indices.tracked_index import Track, univariate_overlap, multivariate_overlap, get_item


class TestBgzfIndex(unittest.TestCase):
    def test_univariate_overlap(self):
        self.assertFalse(univariate_overlap(4, 5))
        self.assertTrue(univariate_overlap(5, 5))
        self.assertFalse(univariate_overlap(6, 5))
        self.assertFalse(univariate_overlap(5, 6))
        self.assertFalse(univariate_overlap(5, 4))

        self.assertFalse(univariate_overlap(4, Interval(5, 10)))
        self.assertTrue(univariate_overlap(5, Interval(5, 10)))
        self.assertTrue(univariate_overlap(9, Interval(5, 10)))
        self.assertFalse(univariate_overlap(10, Interval(5, 10)))
        self.assertFalse(univariate_overlap(Interval(5, 10), 4))
        self.assertTrue(univariate_overlap(Interval(5, 10), 5))
        self.assertTrue(univariate_overlap(Interval(5, 10), 9))
        self.assertFalse(univariate_overlap(Interval(5, 10), 10))

        self.assertFalse(univariate_overlap(Interval(0, 5), Interval(5, 10)))
        self.assertTrue(univariate_overlap(Interval(0, 6), Interval(5, 10)))
        self.assertTrue(univariate_overlap(Interval(0, 10), Interval(5, 10)))
        self.assertTrue(univariate_overlap(Interval(5, 6), Interval(5, 10)))
        self.assertTrue(univariate_overlap(Interval(5, 10), Interval(5, 10)))
        self.assertFalse(univariate_overlap(Interval(10, 11), Interval(5, 10)))

    def test_multivariate_overlap(self):
        self.assertFalse(multivariate_overlap(['chr1', Interval(0, 10)], ['chr1', Interval(10, 20)]))
        self.assertTrue(multivariate_overlap(['chr1', Interval(0, 11)], ['chr1', Interval(10, 20)]))
        self.assertFalse(multivariate_overlap([Interval('chr1', 'chr2'), Interval(0, 10)],
                                              [Interval('chr3', 'chr4'), Interval(0, 10)]))
        self.assertTrue(multivariate_overlap([Interval('chr1', 'chr2'), Interval(0, 10)],
                                              [Interval('chr2', 'chr3'), Interval(0, 10)]))

    def test_get_item(self):
        starts = ['chr1', 500]
        stops = ['chr1', 1500]
        self.assertEquals(['chr1', Interval(500, 1500)], get_item(starts, stops))

    def test_get_start_stop(self):
        track = Track(2)
        start, stop = track.get_start_stop(['chr1', Interval(500, 1500)])
        self.assertEquals(['chr1', 500], start)
        self.assertEquals(['chr1', 1500], stop)
        start, stop = track.get_start_stop(['chr1', 500, 1500])
        self.assertEquals(['chr1', 500], start)
        self.assertEquals(['chr1', 1500], stop)

    def test_get_overlapping_bounds(self):
        track = Track(2)
        track.starts = [['chr1', 1000], ['chr1', 3000], ['chr2', 1000], ['chr2', 3000]]
        track.stops = [['chr1', 2000], ['chr1', 4000], ['chr2', 2000], ['chr2', 4000]]
        self.assertEquals((0, 0), track.get_overlapping_bounds(['chr1', 0], ['chr1', 0]))
        self.assertEquals((0, 0), track.get_overlapping_bounds(['chr1', 0], ['chr1', 1000]))
        self.assertEquals((0, 1), track.get_overlapping_bounds(['chr1', 0], ['chr1', 1001]))
        self.assertEquals((0, 1), track.get_overlapping_bounds(['chr1', 0], ['chr1', 3000]))
        self.assertEquals((0, 2), track.get_overlapping_bounds(['chr1', 0], ['chr1', 3001]))
        self.assertEquals((0, 2), track.get_overlapping_bounds(['chr1', 0], ['chr1', 4001]))
        self.assertEquals((0, 2), track.get_overlapping_bounds(['chr1', 0], ['chr2', 0]))
        self.assertEquals((0, 2), track.get_overlapping_bounds(['chr1', 0], ['chr2', 1000]))
        self.assertEquals((0, 3), track.get_overlapping_bounds(['chr1', 0], ['chr2', 1001]))
        self.assertEquals((0, 3), track.get_overlapping_bounds(['chr1', 0], ['chr2', 3000]))
        self.assertEquals((0, 4), track.get_overlapping_bounds(['chr1', 0], ['chr2', 3001]))
        self.assertEquals((0, 4), track.get_overlapping_bounds(['chr1', 0], ['chr2', 4001]))
        self.assertEquals((0, 4), track.get_overlapping_bounds(['chr1', 1999], ['chr2', 4001]))
        self.assertEquals((1, 4), track.get_overlapping_bounds(['chr1', 2000], ['chr2', 4001]))
        self.assertEquals((1, 4), track.get_overlapping_bounds(['chr1', 3999], ['chr2', 4001]))
        self.assertEquals((2, 4), track.get_overlapping_bounds(['chr1', 4000], ['chr2', 4001]))
        self.assertEquals((2, 4), track.get_overlapping_bounds(['chr2', 0], ['chr2', 4001]))
        self.assertEquals((2, 4), track.get_overlapping_bounds(['chr2', 1999], ['chr2', 4001]))
        self.assertEquals((3, 4), track.get_overlapping_bounds(['chr2', 2000], ['chr2', 4001]))
        self.assertEquals((3, 4), track.get_overlapping_bounds(['chr2', 3999], ['chr2', 4001]))
        self.assertEquals((4, 4), track.get_overlapping_bounds(['chr2', 4000], ['chr2', 4001]))

    def test_fetch(self):
        track = Track(2)
        track.starts = [['chr1', 1000], ['chr1', 3000], ['chr2', 1000], ['chr2', 3000]]
        track.stops = [['chr1', 2000], ['chr1', 4000], ['chr2', 2000], ['chr2', 4000]]
        track.offsets = [[0, 2], [3, 5], [6, 8], [9, 11]]

        self.assertEquals([[0, 2], [3, 5]],
                          track.fetch('chr1', Interval(1750, 3250)))
        self.assertEquals([[0, 2], [3, 5]],
                          track.fetch('chr1', 1750, 3250))

    def test_get_cost_increase(self):
        track = Track(2)
        self.assertEquals(2, track.get_cost_increase(['chr1', Interval(0, 1000)], bgzf.make_virtual_offset(0, 12)))


class TestTrackAdd(unittest.TestCase):
    def setUp(self):
        self.track = Track(2)
        self.track.starts = [['chr1', 1000], ['chr1', 3000], ['chr2', 1000], ['chr2', 3000]]
        self.track.stops = [['chr1', 2000], ['chr1', 4000], ['chr2', 2000], ['chr2', 4000]]
        self.track.offsets = [[0, 2], [3, 5], [6, 8], [9, 11]]

    def test_add_before(self):
        self.assertRaises(ValueError, self.track.add, ['chr1', Interval(0, 1000)], 6)

    def test_add_overlap_earlier_offset(self):
        self.assertRaises(ValueError, self.track.add, ['chr2', Interval(3500, 4500)], 10)

    def test_add_overlap_same_offset(self):
        self.track.add(['chr2', Interval(3500, 4500)], 11)

        self.assertEquals([['chr1', 1000], ['chr1', 3000], ['chr2', 1000], ['chr2', 3000]], self.track.starts)
        self.assertEquals([['chr1', 2000], ['chr1', 4000], ['chr2', 2000], ['chr2', 4500]], self.track.stops)
        self.assertEquals([[0, 2], [3, 5], [6, 8], [9, 11]], self.track.offsets)

    def test_add_overlap_later_offset(self):
        self.track.add(['chr2', Interval(3500, 4500)], 12)

        self.assertEquals([['chr1', 1000], ['chr1', 3000], ['chr2', 1000], ['chr2', 3000]], self.track.starts)
        self.assertEquals([['chr1', 2000], ['chr1', 4000], ['chr2', 2000], ['chr2', 4500]], self.track.stops)
        self.assertEquals([[0, 2], [3, 5], [6, 8], [9, 12]], self.track.offsets)

    def test_add_after(self):
        self.track.add(['chr2', Interval(5000, 6000)], 11)

        self.assertEquals([['chr1', 1000], ['chr1', 3000], ['chr2', 1000], ['chr2', 3000], ['chr2', 5000]], self.track.starts)
        self.assertEquals([['chr1', 2000], ['chr1', 4000], ['chr2', 2000], ['chr2', 4000], ['chr2', 6000]], self.track.stops)
        self.assertEquals([[0, 2], [3, 5], [6, 8], [9, 11], [11, 11]], self.track.offsets)

    def test_get_cost_increase(self):
        self.assertRaises(ValueError, self.track.get_cost_increase, ['chr2', Interval(0, 1000)], 11)
        self.assertRaises(ValueError, self.track.get_cost_increase, ['chr2', Interval(5000, 6000)], 10)
        self.assertAlmostEquals(0, self.track.get_cost_increase(['chr2', Interval(3500, 4500)],
                                                                        bgzf.make_virtual_offset(0, 11)))
        self.assertAlmostEquals(1, self.track.get_cost_increase(['chr2', Interval(3500, 4500)],
                                                                        bgzf.make_virtual_offset(1, 11)))
        self.assertAlmostEquals(0.3219281, self.track.get_cost_increase(['chr2', Interval(5000, 6000)],
                                                                bgzf.make_virtual_offset(0, 11)))
        self.assertAlmostEquals(0.3219281, self.track.get_cost_increase(['chr2', Interval(5000, 6000)],
                                                                bgzf.make_virtual_offset(1, 11)))

if __name__ == '__main__':
    unittest.main()
