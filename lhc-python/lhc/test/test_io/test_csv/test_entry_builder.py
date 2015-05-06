import unittest

from collections import namedtuple
from lhc.io.csv_ import EntryBuilder


class TestEntryBuilder(unittest.TestCase):
    def test_builder_columns(self):
        builder1 = EntryBuilder(int, columns=[4])
        builder2 = EntryBuilder(float, columns=[4])

        self.assertEquals(5, builder1(['1', '2', '3', '4', '5']))
        self.assertAlmostEquals(5.5, builder2(['1.1', '2.2', '3.3', '4.4', '5.5']))

    def test_builder_builders(self):
        builder = EntryBuilder(namedtuple('X', ['a', 'b', 'c']),
                               builders=[
                                   EntryBuilder(int, columns=[1]),
                                   EntryBuilder(slice, builders=[
                                       EntryBuilder(int, columns=[2]),
                                       EntryBuilder(int, columns=[3])])],
                               columns=[4])

        res = builder(['x', '5', '10', '20', 'test'])

        self.assertEquals(5, res.a)
        self.assertEquals(slice(10, 20), res.b)
        self.assertEquals('test', res.c)

if __name__ == '__main__':
    unittest.main()
