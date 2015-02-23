import unittest

from lhc.collections import SortedList


class TestSortedList(unittest.TestCase):
    def test_init(self):
        sl = SortedList([4, 2, 5, 1, 6, 3])

        self.assertEquals([1, 2, 3, 4, 5, 6], list(iter(sl)))

    def test_init_key(self):
        sl = SortedList([(1, 4), (2, 2), (3, 5), (4, 1), (5, 6), (6, 3)], key=lambda x: x[1])

        self.assertEquals([(4, 1), (2, 2), (6, 3), (1, 4), (3, 5), (5, 6)], list(iter(sl)))

    def test_init_reversed(self):
        sl = SortedList([4, 2, 5, 1, 6, 3], reversed=True)

        self.assertEquals([6, 5, 4, 3, 2, 1], list(iter(sl)))

    def test_add(self):
        sl = SortedList([4, 2, 5, 1, 6, 3])

        sl.add(4.5)

        self.assertEquals([1, 2, 3, 4, 4.5, 5, 6], list(iter(sl)))

    def test_add_key(self):
        sl = SortedList([(1, 4), (2, 2), (3, 5), (4, 1), (5, 6), (6, 3)], key=lambda x: x[1])

        sl.add((7, 4.5))

        self.assertEquals([(4, 1), (2, 2), (6, 3), (1, 4), (7, 4.5), (3, 5), (5, 6)], list(iter(sl)))


    def test_add_reversed(self):
        sl = SortedList([4, 2, 5, 1, 6, 3], reversed=True)

        sl.add(2.5)

        self.assertEquals([6, 5, 4, 3, 2.5, 2, 1], list(iter(sl)))

    def test_add_key_reversed(self):
        sl = SortedList([(1, 4), (2, 2), (3, 5), (4, 1), (5, 6), (6, 3)], key=lambda x: x[1], reversed=True)

        sl.add((7, 4.5))

        self.assertEquals([(5, 6), (3, 5), (7, 4.5), (1, 4), (6, 3), (2, 2), (4, 1)], list(iter(sl)))


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())