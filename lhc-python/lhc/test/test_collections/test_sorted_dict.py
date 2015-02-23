import unittest

from lhc.collections import SortedDict


class TestSortedDict(unittest.TestCase):
    def test_init(self):
        sd = SortedDict([(2, 'a'), (3, 'b'), (1, 'c')])

        self.assertEqual(list(sd.iteritems()), [(1, 'c'), (2, 'a'), (3, 'b')])

    def test_setGet(self):
        sd = SortedDict()
        sd[1] = 'b'
        sd[3] = 'c'
        sd[2] = 'a'
        
        self.assertEquals(sd[1], 'b')
        self.assertEquals(sd[2], 'a')
        self.assertEquals(sd[3], 'c')
    
    def test_popHighest(self):
        sd = SortedDict()
        sd[1] = 'b'
        sd[3] = 'c'
        sd[2] = 'a'
        
        self.assertEquals(sd.pop_highest(), (3, 'c'))
    
    def test_popLowest(self):
        sd = SortedDict()
        sd[1] = 'b'
        sd[3] = 'c'
        sd[2] = 'a'
        
        self.assertEquals(sd.pop_lowest(), (1, 'b'))
    
    def test_iterKeys(self):
        sd = SortedDict()
        sd[1] = 'b'
        sd[3] = 'c'
        sd[2] = 'a'
        
        it = iter(sd)
        
        self.assertEquals(it.next(), 1)
        self.assertEquals(it.next(), 2)
        self.assertEquals(it.next(), 3)
        
    def test_iterValues(self):
        sd = SortedDict()
        sd[1] = 'b'
        sd[3] = 'c'
        sd[2] = 'a'
        
        it = sd.itervalues()
        
        self.assertEquals(it.next(), 'b')
        self.assertEquals(it.next(), 'a')
        self.assertEquals(it.next(), 'c')

if __name__ == "__main__":
    unittest.main()
