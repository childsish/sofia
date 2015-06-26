__author__ = 'Liam Childs'

import unittest

from lhc.interval import Interval as I
from lhc.collections.interval_tracker import IntervalTracker


class TestTracker(unittest.TestCase):
    def test_init(self):
        tracker = IntervalTracker([I(0, 25, 0), I(0, 5, 0), I(10, 15, 1), I(20, 25, 2)])

        self.assertEquals(2, len(tracker.tracks))
        self.assertEquals([0], tracker.tracks[0].starts)
        self.assertEquals([25], tracker.tracks[0].stops)
        self.assertEquals([{0}], tracker.tracks[0].blocks)
        self.assertEquals([10, 20], tracker.tracks[1].starts)
        self.assertEquals([15, 25], tracker.tracks[1].stops)
        self.assertEquals([{1}, {2}], tracker.tracks[1].blocks)

    def test_contains(self):
        tracker = IntervalTracker([I(0, 25, 0), I(0, 5, 0), I(10, 15, 1), I(20, 25, 2)])

        self.assertIn(I(5, 10), tracker)
        self.assertNotIn(I(25, 30), tracker)

    def test_getitem(self):
        tracker = IntervalTracker([I(0, 25, 0), I(0, 5, 0), I(10, 15, 1), I(20, 25, 2)])

        self.assertEquals({0}, tracker[0:5])
        self.assertEquals({0, 2}, tracker[20:25])

    def test_setitem_nonoverlapping_new_block(self):
        tracker = IntervalTracker([I(0, 25, 0), I(0, 5, 0), I(10, 15, 1), I(20, 25, 2)])

        tracker[30:35] = 3

        self.assertEquals(2, len(tracker.tracks[0].starts))
        self.assertEquals(2, len(tracker.tracks[1].starts))

    def test_setitem_nonoverlapping_existing_block(self):
        tracker = IntervalTracker([I(0, 25, 0), I(0, 5, 0), I(10, 15, 1), I(20, 25, 2)])

        tracker[30:35] = 2

        self.assertEquals(2, len(tracker.tracks[0].starts))
        self.assertEquals(2, len(tracker.tracks[1].starts))

    def test_setitem_overlapping_new_block(self):
        tracker = IntervalTracker([I(0, 25, 0), I(0, 5, 0), I(10, 15, 1), I(20, 25, 2)])

        tracker[24:35] = 3

        self.assertEquals(1, len(tracker.tracks[0].starts))
        self.assertEquals(2, len(tracker.tracks[1].starts))

    def test_setitem_overlapping_existing_block(self):
        tracker = IntervalTracker([I(0, 25, 0), I(0, 5, 0), I(10, 15, 1), I(20, 25, 2)])

        tracker[24:35] = 2

        self.assertEquals(1, len(tracker.tracks[0].starts))
        self.assertEquals(2, len(tracker.tracks[1].starts))


if __name__ == '__main__':
    unittest.main()
