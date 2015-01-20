import unittest

from lhc.collections.interval_tree import IntervalTree

class TestIntervalTree(unittest.TestCase):
    def test_init(self):
        ivls = [slice(0, 10), slice(2, 30), slice(3, 20), slice(5, 7), slice(9, 15), slice(20, 25), slice(21, 22), slice(25, 31), slice(35, 39), slice(36, 39)]
        tree = IntervalTree(ivls)
        
        self.assertEquals(tree.left, None)
        self.assertEquals(tree.right, None)
        self.assertEquals(tree.ivls, ivls)
        
    def test_initDeepTree(self):
        ivls = [slice(0, 10), slice(2, 30), slice(3, 20), slice(5, 7), slice(9, 15), slice(20, 25), slice(21, 22), slice(25, 31), slice(35, 39), slice(36, 39)]
        tree = IntervalTree(ivls, minbucket=1)
        
        self.assertEquals(set(map(str, tree.ivls)), set(map(str, [slice(2, 30), slice(3, 20)])))
        self.assertAlmostEquals(tree.mid, 19.5)
        self.assertEquals(set(map(str, tree.left.ivls)), set(map(str, [slice(0, 10), slice(5, 7), slice(9, 15)])))
        self.assertEquals(set(map(str, tree.right.ivls)), set(map(str, [slice(20, 25), slice(21, 22), slice(25, 31), slice(35, 39), slice(36, 39)])))
        self.assertIsNone(tree.left.left)
        self.assertIsNone(tree.left.right)
        self.assertIsNone(tree.right.left)
        self.assertIsNone(tree.right.right)
    
    def test_intersect(self):
        ivls = [slice(0, 10), slice(2, 30), slice(3, 20), slice(5, 7), slice(9, 15), slice(20, 25), slice(21, 22), slice(25, 31), slice(35, 39), slice(36, 39)]
        tree = IntervalTree(ivls)
        self.assertEquals(set(map(str, tree.intersect(slice(15, 30)))),
            set(map(str, [slice(2, 30, None), slice(3, 20, None), slice(20, 25, None), slice(21, 22, None), slice(25, 31, None)])))

if __name__ == '__main__':
    unittest.main()
