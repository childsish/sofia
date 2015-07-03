__author__ = 'Liam Childs'

import unittest

from lhc.indices.bgzf import PointIndex

class TestPointIndex(unittest.TestCase):
    def setUp(self):
        self.index = PointIndex()
        self.index.add([5], 0)
        self.index.add([10], 0)
        self.index.add([15], 1)
        self.index.add([20], 2)

    def test_contains(self):
        self.assertIn([5], self.index)
        self.assertIn([10], self.index)
        self.assertIn([15], self.index)
        self.assertIn([20], self.index)

        self.assertNotIn([4], self.index)
        self.assertNotIn([6], self.index)
        self.assertNotIn([9], self.index)
        self.assertNotIn([11], self.index)
        self.assertNotIn([14], self.index)
        self.assertNotIn([16], self.index)
        self.assertNotIn([19], self.index)
        self.assertNotIn([21], self.index)

    def test_add(self):
        self.index.add([0], 3)
        self.index.add([12], 3)
        self.index.add([25], 3)

        self.assertEquals([0, 5, 10, 12, 15, 20, 25], self.index.keys)
        self.assertEquals([{3}, {0}, {0}, {3}, {1}, {2}, {3}], self.index.values)

    def test_fetch(self):
        self.assertRaises(KeyError, self.index.fetch, 4)
        self.assertEquals({0}, self.index.fetch(5))
        self.assertRaises(KeyError, self.index.fetch, 6)
        self.assertRaises(KeyError, self.index.fetch, 9)
        self.assertEquals({0}, self.index.fetch(10))
        self.assertRaises(KeyError, self.index.fetch, 11)
        self.assertRaises(KeyError, self.index.fetch, 14)
        self.assertEquals({1}, self.index.fetch(15))
        self.assertRaises(KeyError, self.index.fetch, 16)
        self.assertRaises(KeyError, self.index.fetch, 19)
        self.assertEquals({2}, self.index.fetch(20))
        self.assertRaises(KeyError, self.index.fetch, 21)

    def test_fetch_extraarg(self):
        self.assertEquals({0, 1, 2}, self.index.fetch(5, 20))

    def test_compress(self):
        index = self.index.compress()

        self.assertEquals([5, 15, 20], index.keys)
        self.assertEquals([{0}, {1}, {2}], index.values)

    def test_compress_factor(self):
        index = self.index.compress(factor=2)

        self.assertEquals([5, 15], index.keys)
        self.assertEquals([{0}, {1, 2}], index.values)


if __name__ == '__main__':
    unittest.main()
