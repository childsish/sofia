__author__ = 'Liam Childs'

import unittest

from lhc.interval import Interval
from lhc.collections.tracked_set import Track, univariate_overlap, multivariate_overlap, get_item


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
        track.items = [[['chr1', Interval(1000, 1500)], ['chr1', Interval(1250, 1750)], ['chr1', Interval(1500, 2000)]],
                       [['chr1', Interval(3000, 3500)], ['chr1', Interval(3250, 3750)], ['chr1', Interval(3500, 4000)]],
                       [['chr2', Interval(1000, 1500)], ['chr2', Interval(1250, 1750)], ['chr2', Interval(1500, 2000)]],
                       [['chr2', Interval(3000, 3500)], ['chr2', Interval(3250, 3750)], ['chr2', Interval(3500, 4000)]]]
        self.assertEquals([['chr1', Interval(1500, 2000)], ['chr1', Interval(3000, 3500)]],
                          track.fetch('chr1', Interval(1750, 3250)))
        self.assertEquals([['chr1', Interval(1500, 2000)], ['chr1', Interval(3000, 3500)]],
                          track.fetch('chr1', 1750, 3250))

    def test_get_cost_increase(self):
        track = Track(2)
        self.assertEquals(2, track.get_cost_increase(['chr1', Interval(0, 1000)]))


class TestTrackAdd(unittest.TestCase):
    def setUp(self):
        self.track = Track(2)
        self.track.starts = [['chr1', 1000], ['chr1', 3000], ['chr2', 1000], ['chr2', 3000]]
        self.track.stops = [['chr1', 2000], ['chr1', 4000], ['chr2', 2000], ['chr2', 4000]]
        self.track.items = [[['chr1', Interval(1000, 1500)], ['chr1', Interval(1250, 1750)], ['chr1', Interval(1500, 2000)]],
                       [['chr1', Interval(3000, 3500)], ['chr1', Interval(3250, 3750)], ['chr1', Interval(3500, 4000)]],
                       [['chr2', Interval(1000, 1500)], ['chr2', Interval(1250, 1750)], ['chr2', Interval(1500, 2000)]],
                       [['chr2', Interval(3000, 3500)], ['chr2', Interval(3250, 3750)], ['chr2', Interval(3500, 4000)]]]

    def test_add_before(self):
        self.track.add(['chr1', Interval(0, 1000)])

        self.assertEquals([['chr1', 0], ['chr1', 1000], ['chr1', 3000], ['chr2', 1000], ['chr2', 3000]], self.track.starts)
        self.assertEquals([['chr1', 1000], ['chr1', 2000], ['chr1', 4000], ['chr2', 2000], ['chr2', 4000]], self.track.stops)
        self.assertEqual(['chr1', Interval(0, 1000)], self.track.items[0][0])

    def test_add_overlap(self):
        self.track.add(['chr1', Interval(0, 1001)])

        self.assertEquals([['chr1', 0], ['chr1', 3000], ['chr2', 1000], ['chr2', 3000]], self.track.starts)
        self.assertEquals([['chr1', 2000], ['chr1', 4000], ['chr2', 2000], ['chr2', 4000]], self.track.stops)
        self.assertEqual(['chr1', Interval(0, 1001)], self.track.items[0][-1])

    def test_add_overlap_multiple_deep(self):
        self.track.add(['chr1', Interval(1999, 3001)])

        self.assertEquals([['chr1', 1000], ['chr2', 1000], ['chr2', 3000]], self.track.starts)
        self.assertEquals([['chr1', 4000], ['chr2', 2000], ['chr2', 4000]], self.track.stops)
        self.assertEqual(['chr1', Interval(1999, 3001)], self.track.items[0][-1])

    def test_add_overlap_multiple_shallow(self):
        self.track.add([Interval('chr1', 'chr3'), Interval(0, 5000)])

        self.assertEquals([['chr1', 0]], self.track.starts)
        self.assertEquals([['chr3', 5000]], self.track.stops)
        self.assertEquals([Interval('chr1', 'chr3'), Interval(0, 5000)], self.track.items[0][-1])

    def test_get_cost_increase(self):
        self.assertAlmostEquals(0.3219281, self.track.get_cost_increase(['chr1', Interval(0, 1000)]))
        self.assertAlmostEquals(1, self.track.get_cost_increase(['chr1', Interval(0, 1001)]))
        self.assertAlmostEquals(3.5849625, self.track.get_cost_increase(['chr1', Interval(1999, 3001)]))
        self.assertAlmostEquals(8, self.track.get_cost_increase([Interval('chr1', 'chr3'), Interval(0, 5000)]))

if __name__ == '__main__':
    unittest.main()
