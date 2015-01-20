import unittest

from lhc.collection.sorted_set import SortedSet

class TestSortedSet(unittest.TestCase):

    def test_setGet(self):
        ss = SortedSet()
        ss.add('b')
        ss.add('c')
        ss.add('a')
        ss.add('b')
        
        self.assertIn('a', ss)
        self.assertIn('b', ss)
        self.assertIn('c', ss)
    
    def test_iter(self):
        ss = SortedSet()
        ss.add('b')
        ss.add('c')
        ss.add('a')
        ss.add('b')
        
        it = iter(ss)
        
        self.assertEquals(it.next(), 'a')
        self.assertEquals(it.next(), 'b')
        self.assertEquals(it.next(), 'c')
        
    
    def test_pop(self):
        ss = SortedSet()
        ss.add('b')
        ss.add('c')
        ss.add('a')
        ss.add('b')
        
        self.assertEquals(ss.pop(), 'c')
        self.assertEquals(ss.pop(), 'b')
        self.assertEquals(ss.pop(), 'a')
    
    def test_index(self):
        ss = SortedSet()
        ss.add('b')
        ss.add('c')
        ss.add('a')
        ss.add('b')
        
        self.assertEquals(ss[0], 'a')
        self.assertEquals(ss[1], 'b')
        self.assertEquals(ss[2], 'c')

if __name__ == "__main__":
    unittest.main()
