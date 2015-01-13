import unittest

from lhc.collection.sorted_dict import SortedDict

class TestSortedDict(unittest.TestCase):

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
        
        self.assertEquals(sd.popHighest(), (3, 'c'))
    
    def test_popLowest(self):
        sd = SortedDict()
        sd[1] = 'b'
        sd[3] = 'c'
        sd[2] = 'a'
        
        self.assertEquals(sd.popLowest(), (1, 'b'))
    
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
