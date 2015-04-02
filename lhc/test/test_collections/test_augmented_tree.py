import unittest

from lhc.collections.augmented_tree import AugmentedTree
from lhc.interval import Interval


class TestAugmentedTree(unittest.TestCase):
    def test_init(self):
        ivls = [Interval(0, 10), Interval(2, 30), Interval(3, 20), Interval(5, 7), Interval(9, 15), Interval(20, 25),
                Interval(21, 22), Interval(25, 31), Interval(35, 39), Interval(36, 39)]
        tree = AugmentedTree(ivls)
        
        self.assertEquals([10, 30, 30, 7, 15, 39, 22, 31, 39, 39], tree.stops)
    
    def test_intersect(self):
        ivls = [Interval(0, 10), Interval(2, 30), Interval(3, 20), Interval(5, 7), Interval(9, 15), Interval(20, 25),
                Interval(21, 22), Interval(25, 31), Interval(35, 39), Interval(36, 39)]
        tree = AugmentedTree(ivls)
        self.assertEquals({Interval(2, 30), Interval(3, 20), Interval(20, 25), Interval(21, 22), Interval(25, 31)},
                          set(tree.intersect(Interval(15, 30))))

if __name__ == '__main__':
    unittest.main()
