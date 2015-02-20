import unittest

from lhc.interval import Interval


class TestInterval(unittest.TestCase):
    def test_get_rel_pos(self):
        ivl = Interval(100, 200)

        self.assertEquals(0, ivl.get_rel_pos(100))
        self.assertEquals(99, ivl.get_rel_pos(199))
        self.assertRaises(IndexError, ivl.get_rel_pos, 99)
        self.assertRaises(IndexError, ivl.get_rel_pos, 200)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
