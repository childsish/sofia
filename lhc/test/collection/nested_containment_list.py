import os
import unittest
import numpy as np

from tempfile import mkstemp
from lhc.collection.nested_containment_list import NestedContainmentList as NCList, getTables

class Test(unittest.TestCase):
    def setUp(self):
        self.hndl, self.fname = mkstemp()
        os.close(self.hndl)
    
    def test_getTables(self):
        ivls = [slice(0, 10), slice(2, 30), slice(3, 20), slice(5, 7), slice(9, 15), slice(20, 25), slice(21, 22), slice(25, 31), slice(35, 39), slice(36, 39)]
        
        ivl_table, grp_table = getTables(ivls)
        
        self.assertEquals(ivl_table.tolist(), [[0, 10, -1], [2, 30, 1], [25, 31, -1], [35, 39, 4], [3, 20, 2], [20, 25, 3], [5, 7, -1], [9, 15, -1], [21, 22, -1], [36, 39, -1]])
        self.assertEquals(grp_table.tolist(), [[0, 4], [4, 2], [6, 2], [8, 1], [9, 1]])
    
    def test_getTablesWithRoot(self):
        ivls = [slice(0, 15), slice(5, 10), slice(20, 25), slice(0, 15), slice(5, 10), slice(20, 25), slice(0, 15), slice(5, 10), slice(20, 25)]
        root = [(0, 3), (3, 3), (6, 3)]
        
        ivl_table, grp_table = getTables(ivls, root)
        
        self.assertEquals(ivl_table.tolist(), [[0, 15, 3], [20, 25, -1], [0, 15, 4], [20, 25, -1], [0, 15, 5], [20, 25, -1], [5, 10, -1], [5, 10, -1], [5, 10, -1]])
        self.assertEquals(grp_table.tolist(), [[0, 2], [2, 2], [4, 2], [6, 1], [7, 1], [8, 1]])
    
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