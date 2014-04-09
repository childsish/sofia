import unittest

from lhc.indices.exact_key import ExactKeyIndex

class Test(unittest.TestCase):
    
    def test_contains(self):
        index = ExactKeyIndex()
        index['a'] = [1, 2, 3]
        
        self.assertTrue('a' in index)
        self.assertFalse('b' in index)
    
    def test_getitem(self):
        index = ExactKeyIndex()
        index['a'] = [1, 2, 3]
        
        self.assertEquals(index['a'], [1, 2, 3])

if __name__ == "__main__":
    unittest.main()
