import unittest

from lhc.indices.exact_string import ExactStringIndex

class Test(unittest.TestCase):
    
    def test_contains(self):
        index = ExactStringIndex()
        index['a'] = [1, 2, 3]
        
        self.assertTrue('a' in index)
        self.assertFalse('b' in index)
    
    def test_getitem(self):
        index = ExactStringIndex()
        index['a'] = [1, 2, 3]
        
        self.assertEquals(index['a'], [1, 2, 3])

if __name__ == "__main__":
    unittest.main()
