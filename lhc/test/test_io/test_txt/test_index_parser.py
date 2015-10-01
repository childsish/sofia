__author__ = 'Liam Childs'

import unittest


from lhc.interval import Interval
from lhc.io.txt_ import IndexParser, Entity, Column
from lhc.indices.bgzf import PointIndex, IntervalIndex


class TestIndexParser(unittest.TestCase):
    def test_parse(self):
        parser = IndexParser()
        index = parser.parse(Entity(tuple, [Column(int, 1), Column(float, 2), Entity(Interval, [Column(int, 3), Column(int, 4)])], 'Entry'))
        self.assertIsInstance(index, PointIndex)
        self.assertEqual((PointIndex, IntervalIndex), index.index_classes)


if __name__ == '__main__':
    unittest.main()
