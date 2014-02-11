import os
import unittest
import numpy as np

from tempfile import mkstemp
from lhc.collection.nested_containment_list import NestedContainmentList as NCList

class Test(unittest.TestCase):
    def setUp(self):
        self.hndl, self.fname = mkstemp()
        os.close(self.hndl)
    
    def test_init(self):
        ivls = [slice(0, 10), slice(2, 30), slice(3, 20), slice(5, 7), slice(9, 15), slice(20, 25), slice(21, 22), slice(25, 31), slice(35, 39), slice(36, 39)]
        
        nclist = NCList(self.fname, ivls)
        
        self.assertEquals(nclist.root.variables['ivls'][:].tolist(), [[0, 10, -1], [2, 30, 1], [25, 31, -1], [35, 39, 4], [3, 20, 2], [20, 25, 3], [5, 7, -1], [9, 15, -1], [21, 22, -1], [36, 39, -1]])
        self.assertEquals(nclist.root.variables['grps'][:].tolist(), [[0, 4], [4, 2], [6, 2], [8, 1], [9, 1]])
        nclist.close()
    
    def test_intersect(self):
        ivls = [slice(0, 10), slice(2, 30), slice(3, 20), slice(5, 7), slice(9, 15), slice(20, 25), slice(21, 22), slice(25, 31), slice(35, 39), slice(36, 39)]
        
        nclist = NCList(self.fname, ivls)
        
        self.assertEquals(set(map(str, nclist.intersect(slice(15, 30)))),
            set(map(str, [slice(2, 30, None), slice(3, 20, None), slice(20, 25, None), slice(21, 22, None), slice(25, 31, None)])))
        nclist.close()

if __name__ == "__main__":
    unittest.main()