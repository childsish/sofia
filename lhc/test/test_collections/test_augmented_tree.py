import unittest

from lhc.collections.augmented_tree import AugmentedTree


class TestAugmentedTree(unittest.TestCase):
    def test_init(self):
        ivls = [slice(0, 10), slice(2, 30), slice(3, 20), slice(5, 7), slice(9, 15), slice(20, 25), slice(21, 22), slice(25, 31), slice(35, 39), slice(36, 39)]
        tree = AugmentedTree(ivls)
        
        self.assertEquals(tree.stops, [10, 30, 30, 7, 15, 39, 22, 31, 39, 39])
    
    def test_intersect(self):
        ivls = [slice(0, 10), slice(2, 30), slice(3, 20), slice(5, 7), slice(9, 15), slice(20, 25), slice(21, 22), slice(25, 31), slice(35, 39), slice(36, 39)]
        tree = AugmentedTree(ivls)
        self.assertEquals(set(map(str, tree.intersect(slice(15, 30)))),
            set(map(str, [slice(2, 30, None), slice(3, 20, None), slice(20, 25, None), slice(21, 22, None), slice(25, 31, None)])))

if __name__ == '__main__':
    unittest.main()
