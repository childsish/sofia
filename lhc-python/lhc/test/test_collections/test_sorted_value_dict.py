import unittest

from lhc.collections import SortedValueDict


class TestSortedValueDict(unittest.TestCase):
    def test_init(self):
        svd = SortedValueDict([(1, 'b'), (2, 'c'), (3, 'a')])

        self.assertEqual([3, 1, 2], list(svd.iterkeys()))
        self.assertEqual(['a', 'b', 'c'], svd.values)

    def test_setitem(self):
        svd = SortedValueDict()
        svd['a'] = 3
        svd['b'] = 1
        svd['c'] = 2

        self.assertEqual(['b', 'c', 'a'], list(svd.iterkeys()))
        self.assertEqual([1, 2, 3], svd.values)
    
    def test_pop_highest(self):
        svd = SortedValueDict([(1, 'b'), (2, 'c'), (3, 'a')])
        
        self.assertEquals((2, 'c'), svd.pop_highest())
    
    def test_pop_lowest(self):
        svd = SortedValueDict([(1, 'b'), (2, 'c'), (3, 'a')])
        
        self.assertEquals((3, 'a'), svd.pop_lowest())
        self.assertEquals('c', svd[2])

    def test_update_value(self):
        svd = SortedValueDict([(1, 'b'), (2, 'c'), (3, 'a')])

        svd[3] = 'd'

        self.assertEqual((3, 'd'), svd.pop_highest())

    def test_mutate_value(self):
        svd = SortedValueDict([(1, [2, 3]), (2, [2, 4]), (3, [1, 2])])

        svd[3][0] = 3

        self.assertEqual((3, [3, 2]), svd.pop_highest())

    def test_mutate_value_member(self):
        svd = SortedValueDict([(1, [[2], 3]), (2, [[2], 4]), (3, [[1], 2])])

        svd[3][0][0] = 3

        self.assertEqual((3, [[3], 2]), svd.pop_highest())

    def test_key(self):
        svd = SortedValueDict([(1, [2, 3]), (2, [2, 4]), (3, [1, 2])], key=lambda x: x[1])

        self.assertEqual((2, [2, 4]), svd.pop_highest())

    def test_key_with_mutate(self):
        svd = SortedValueDict([(1, [2, 3]), (2, [2, 4]), (3, [1, 2])], key=lambda x: x[1])

        svd[3][1] = 5

        self.assertEqual((3, [1, 5]), svd.pop_highest())

    def test_value_with_functions(self):
        svd = SortedValueDict([(1, [2, 3]), (2, [2, 4]), (3, [1, 2])], key=lambda x: x[0])

        svd[3].insert(0, 5)

        self.assertEqual((3, [5, 1, 2]), svd.pop_highest())

if __name__ == "__main__":
    unittest.main()
