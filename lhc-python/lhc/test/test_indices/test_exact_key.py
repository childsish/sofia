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
    
    def test_pickle(self):
        index = ExactKeyIndex()
        index['a'] = [1, 2, 3]

        fhndl, fname = tempfile.mkstemp()
        fhndl = os.fdopen(fhndl, 'w')
        cPickle.dump(index, fhndl)
        fhndl.close()
        
        infile = open(fname)
        index = cPickle.load(infile)
        infile.close()
        self.assertEquals(index['a'], [1, 2, 3])
        os.remove(fname)

if __name__ == "__main__":
    unittest.main()
