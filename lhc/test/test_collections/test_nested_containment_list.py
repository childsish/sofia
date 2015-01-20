import os
import unittest
import numpy as np

from tempfile import mkstemp
from lhc.collection import nested_containment_list as ncl

class Test(unittest.TestCase):
    def setUp(self):
        self.hndl, self.fname = mkstemp()
        os.close(self.hndl)
    
    def test__reduceIntervals(self):
        ivls = [slice(150, 350), slice(50, 100), slice(250, 300), slice(0, 200), slice(0, 75), slice(150, 350), slice(250, 300)]
        
        ivls, idxs = ncl._reduceIntervals(ivls)
        
        self.assertEquals(idxs.tolist(), [0, 1, 2, 3, 4, 0, 2])
        self.assertEquals(ivls, [slice(150, 350, None), slice(50, 100, None), slice(250, 300, None), slice(0, 200, None), slice(0, 75, None)])
    
    def test__sortIntervals(self):
        ivls = [slice(150, 350), slice(50, 100), slice(250, 300), slice(0, 200), slice(0, 75), slice(150, 350), slice(250, 300)]
        
        ivls, idx0 = ncl._reduceIntervals(ivls)
        ivls, idx1 = ncl._sortIntervals(ivls)
        
        self.assertEquals(idx1.tolist(), [3, 4, 1, 0, 2])
        self.assertEquals(np.argsort(idx1)[idx0].tolist(), [3, 2, 4, 0, 1, 3, 4]) # Index into reduced and sorted set
        self.assertEquals(ivls, [slice(0, 200, None), slice(0, 75, None), slice(50, 100, None), slice(150, 350, None), slice(250, 300, None)])
    
    def test__getParentIds(self):
        ivls = [slice(150, 350), slice(50, 100), slice(250, 300), slice(0, 200), slice(0, 75), slice(150, 350), slice(250, 300)]
        
        ivls, idx0 = ncl._reduceIntervals(ivls)
        ivls, idx1 = ncl._sortIntervals(ivls)
        parent_idxs = ncl._getParentIdxs(ivls)
        
        self.assertEquals(parent_idxs.tolist(), [-1, 0, 0, -1, 3])
    
    def test__getGroupTable(self):
        ivls = [slice(150, 350), slice(50, 100), slice(250, 300), slice(0, 200), slice(0, 75), slice(150, 350), slice(250, 300)]
        
        ivls, idx0 = ncl._reduceIntervals(ivls)
        ivls, idx1 = ncl._sortIntervals(ivls)
        parent_idxs = ncl._getParentIdxs(ivls)
        grp_table, pnt2grp = ncl._getGroupTable(parent_idxs)
        
        self.assertEquals(grp_table.tolist(), [[0, 2], [2, 2], [4, 1]])
        self.assertEquals(pnt2grp, {-1: 0, 0: 1, 3: 2})
    
    def test__getIntervalTable(self):
        ivls = [slice(150, 350), slice(50, 100), slice(250, 300), slice(0, 200), slice(0, 75), slice(150, 350), slice(250, 300)]
        
        ivls, idx0 = ncl._reduceIntervals(ivls)
        ivls, idx1 = ncl._sortIntervals(ivls)
        parent_idxs = ncl._getParentIdxs(ivls)
        grp_table, pnt2grp = ncl._getGroupTable(parent_idxs)
        ivl_table, idx2 = ncl._getIntervalTable(ivls, pnt2grp, parent_idxs)
        
        self.assertEquals(idx2.tolist(), [0, 3, 1, 2, 4])
        self.assertEquals(np.argsort(idx2)[np.argsort(idx1)[idx0]].tolist(), [1, 3, 4, 0, 2, 1, 4])
        self.assertEquals(ivl_table.tolist(), [[0, 200, 1], [150, 350, 2], [0, 75, -1], [50, 100, -1], [250, 300, -1]])

    def test_getTables(self):
        ivls = [slice(0, 10), slice(2, 30), slice(3, 20), slice(5, 7), slice(9, 15), slice(20, 25), slice(21, 22), slice(25, 31), slice(35, 39), slice(36, 39)]
        
        ivl_table, grp_table, idx = ncl.getTables(ivls)
        
        self.assertEquals(idx.tolist(), [0, 1, 4, 6, 7, 5, 8, 2, 3, 9])
        self.assertEquals(ivl_table.tolist(), [[0, 10, -1], [2, 30, 1], [25, 31, -1], [35, 39, 4], [3, 20, 2], [20, 25, 3], [5, 7, -1], [9, 15, -1], [21, 22, -1], [36, 39, -1]])
        self.assertEquals(grp_table.tolist(), [[0, 4], [4, 2], [6, 2], [8, 1], [9, 1]])
    
    def test_init(self):
        ivls = [slice(0, 10), slice(2, 30), slice(3, 20), slice(5, 7), slice(9, 15), slice(20, 25), slice(21, 22), slice(25, 31), slice(35, 39), slice(36, 39)]
        
        nclist = ncl.NestedContainmentList(self.fname, ivls)
        
        self.assertEquals(nclist.root.variables['ivls'][:].tolist(), [[0, 10, -1], [2, 30, 1], [25, 31, -1], [35, 39, 4], [3, 20, 2], [20, 25, 3], [5, 7, -1], [9, 15, -1], [21, 22, -1], [36, 39, -1]])
        self.assertEquals(nclist.root.variables['grps'][:].tolist(), [[0, 4], [4, 2], [6, 2], [8, 1], [9, 1]])
        nclist.close()
    
    def test_intersect(self):
        ivls = [slice(0, 10), slice(2, 30), slice(3, 20), slice(5, 7), slice(9, 15), slice(20, 25), slice(21, 22), slice(25, 31), slice(35, 39), slice(36, 39)]
        
        nclist = ncl.NestedContainmentList(self.fname, ivls)
        
        self.assertEquals(set(map(str, nclist.intersect(slice(15, 30)))),
            set(map(str, [slice(2, 30, None), slice(3, 20, None), slice(20, 25, None), slice(21, 22, None), slice(25, 31, None)])))
        nclist.close()

if __name__ == "__main__":
    unittest.main()