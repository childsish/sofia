import unittest

from lhc.collections import SortedValueDict


class TestSortedValueDict(unittest.TestCase):
    def test_init(self):
        svd = SortedValueDict([(1, 'b'), (2, 'c'), (3, 'a')])

        self.assertEqual(list(svd.iterkeys()), [3, 1, 2])
        self.assertEqual(svd.values, ['a', 'b', 'c'])

    def test_setitem(self):
        svd = SortedValueDict()
        svd['a'] = 3
        svd['b'] = 1
        svd['c'] = 2

        self.assertEqual(list(svd.iterkeys()), ['b', 'c', 'a'])
        self.assertEqual(svd.values, [1, 2, 3])
    
    def test_pop_highest(self):
        svd = SortedValueDict([(1, 'b'), (2, 'c'), (3, 'a')])
        
        self.assertEquals(svd.pop_highest(), (2, 'c'))
    
    def test_pop_lowest(self):
        svd = SortedValueDict([(1, 'b'), (2, 'c'), (3, 'a')])
        
        self.assertEquals(svd.pop_lowest(), (3, 'a'))

    def test_update_value(self):
        svd = SortedValueDict([(1, 'b'), (2, 'c'), (3, 'a')])

        svd[3] = 'd'

        self.assertEqual(svd.pop_highest(), (3, 'd'))

    def test_mutate_value(self):
        svd = SortedValueDict([(1, [2, 3]), (2, [2, 4]), (3, [1, 2])])

        svd[3][0] = 3

        self.assertEqual(svd.pop_highest(), (3, [3, 2]))

    def test_mutate_value_member(self):
        svd = SortedValueDict([(1, [[2], 3]), (2, [[2], 4]), (3, [[1], 2])])

        svd[3][0][0] = 3

        self.assertEqual(svd.pop_highest(), (3, [[3], 2]))

if __name__ == "__main__":
    unittest.main()
