import unittest

from collections import namedtuple
from lhc.io.csv_ import Entity, Column


class TestEntity(unittest.TestCase):
    def test_column(self):
        row = ['x', '5', '10', 'test']

        self.assertEquals(5, Column(int, 1)(row))
        self.assertAlmostEquals(5, Column(float, 1)(row))
        self.assertEquals('test', Column(str, 3)(row))

    def test_entity(self):
        entity = Entity(namedtuple('X', ['a', 'b', 'c']), [
            Column(int, 1),
            Entity(slice, [
                Column(int, 2),
                Column(int, 3)
            ]),
            Column(str, 4)
        ])

        res = entity(['x', '5', '10', '20', 'test'])

        self.assertEquals(5, res.a)
        self.assertEquals(slice(10, 20), res.b)
        self.assertEquals('test', res.c)

if __name__ == '__main__':
    unittest.main()
