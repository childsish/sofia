import unittest

from collections import namedtuple
from lhc.io.txt_ import EntityFormatter, ColumnFormatter


class TestEntityFormatter(unittest.TestCase):
    def test_column(self):
        row = ['x', '5', '10', 'test']

        self.assertEquals(5, ColumnFormatter(int, 1)(*row))
        self.assertAlmostEquals(5, ColumnFormatter(float, 1)(*row))
        self.assertEquals('test', ColumnFormatter(str, 3)(*row))

    def test_entity(self):
        entity = EntityFormatter(namedtuple('X', ['a', 'b', 'c']), [
            ColumnFormatter(int, 1),
            EntityFormatter(slice, [
                ColumnFormatter(int, 2),
                ColumnFormatter(int, 3)
            ]),
            ColumnFormatter(str, 4)
        ])

        res = entity('x', '5', '10', '20', 'test')

        self.assertEquals(5, res.a)
        self.assertEquals(slice(10, 20), res.b)
        self.assertEquals('test', res.c)

if __name__ == '__main__':
    unittest.main()
