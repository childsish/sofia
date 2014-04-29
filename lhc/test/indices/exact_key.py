import cPickle
import os
import tempfile
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
    
    def test_pickle(self)
        self.fhndl, self.fname = tempfile.mkstemp()
        self.fhndl = os.open(self.fhndl)
        index = ExactKeyIndex()
        index['a'] = [1, 2, 3]
        cPickle.dump(index, self.fhndl)
        os.close(self.fhndl)
        
        infile = open(self.fname)
        index = cPickle.load(infile)
        infile.close()
        self.assertEquals(index['a'], [1, 2, 3])
        os.remove(self.fname)

if __name__ == "__main__":
    unittest.main()
