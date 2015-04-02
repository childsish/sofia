import os
import unittest
import numpy as np

from tempfile import mkstemp
from lhc.collections import nested_containment_list as ncl
from lhc.interval import Interval


class Test(unittest.TestCase):
    def setUp(self):
        self.hndl, self.fname = mkstemp()
        os.close(self.hndl)
    
    def test_reduce_intervals(self):
        ivls = [Interval(150, 350), Interval(50, 100), Interval(250, 300), Interval(0, 200), Interval(0, 75), Interval(150, 350), Interval(250, 300)]
        
        ivls, idxs = ncl._reduce_intervals(ivls)
        
        self.assertEquals(idxs.tolist(), [0, 1, 2, 3, 4, 0, 2])
        self.assertEquals(ivls, [Interval(150, 350), Interval(50, 100), Interval(250, 300), Interval(0, 200), Interval(0, 75)])
    
    def test_sor_iIntervals(self):
        ivls = [Interval(150, 350), Interval(50, 100), Interval(250, 300), Interval(0, 200), Interval(0, 75), Interval(150, 350), Interval(250, 300)]
        
        ivls, idx0 = ncl._reduce_intervals(ivls)
        ivls, idx1 = ncl._sort_intervals(ivls)
        
        self.assertEquals(idx1.tolist(), [3, 4, 1, 0, 2])
        self.assertEquals(np.argsort(idx1)[idx0].tolist(), [3, 2, 4, 0, 1, 3, 4]) # Index into reduced and sorted set
        self.assertEquals(ivls, [Interval(0, 200), Interval(0, 75), Interval(50, 100), Interval(150, 350), Interval(250, 300)])
    
    def test_get_parent_indices(self):
        ivls = [Interval(150, 350), Interval(50, 100), Interval(250, 300), Interval(0, 200), Interval(0, 75), Interval(150, 350), Interval(250, 300)]
        
        ivls, idx0 = ncl._reduce_intervals(ivls)
        ivls, idx1 = ncl._sort_intervals(ivls)
        parent_idxs = ncl._get_parent_indices(ivls)
        
        self.assertEquals(parent_idxs.tolist(), [-1, 0, 0, -1, 3])
    
    def test_get_gorup_table(self):
        ivls = [Interval(150, 350), Interval(50, 100), Interval(250, 300), Interval(0, 200), Interval(0, 75), Interval(150, 350), Interval(250, 300)]
        
        ivls, idx0 = ncl._reduce_intervals(ivls)
        ivls, idx1 = ncl._sort_intervals(ivls)
        parent_idxs = ncl._get_parent_indices(ivls)
        grp_table, pnt2grp = ncl._get_group_table(parent_idxs)
        
        self.assertEquals(grp_table.tolist(), [[0, 2], [2, 2], [4, 1]])
        self.assertEquals(pnt2grp, {-1: 0, 0: 1, 3: 2})
    
    def test_get_interval_table(self):
        ivls = [Interval(150, 350), Interval(50, 100), Interval(250, 300), Interval(0, 200), Interval(0, 75), Interval(150, 350), Interval(250, 300)]
        
        ivls, idx0 = ncl._reduce_intervals(ivls)
        ivls, idx1 = ncl._sort_intervals(ivls)
        parent_idxs = ncl._get_parent_indices(ivls)
        grp_table, pnt2grp = ncl._get_group_table(parent_idxs)
        ivl_table, idx2 = ncl._get_interval_table(ivls, pnt2grp, parent_idxs)
        
        self.assertEquals(idx2.tolist(), [0, 3, 1, 2, 4])
        self.assertEquals(np.argsort(idx2)[np.argsort(idx1)[idx0]].tolist(), [1, 3, 4, 0, 2, 1, 4])
        self.assertEquals(ivl_table.tolist(), [[0, 200, 1], [150, 350, 2], [0, 75, -1], [50, 100, -1], [250, 300, -1]])

    def test_get_tables(self):
        ivls = [Interval(0, 10), Interval(2, 30), Interval(3, 20), Interval(5, 7), Interval(9, 15), Interval(20, 25),
                Interval(21, 22), Interval(25, 31), Interval(35, 39), Interval(36, 39)]
        
        ivl_table, grp_table, idx = ncl.get_tables(ivls)
        
        self.assertEquals(idx.tolist(), [0, 1, 4, 6, 7, 5, 8, 2, 3, 9])
        self.assertEquals(ivl_table.tolist(), [[0, 10, -1], [2, 30, 1], [25, 31, -1], [35, 39, 4], [3, 20, 2], [20, 25, 3], [5, 7, -1], [9, 15, -1], [21, 22, -1], [36, 39, -1]])
        self.assertEquals(grp_table.tolist(), [[0, 4], [4, 2], [6, 2], [8, 1], [9, 1]])
    
    def test_init(self):
        ivls = [Interval(0, 10), Interval(2, 30), Interval(3, 20), Interval(5, 7), Interval(9, 15), Interval(20, 25),
                Interval(21, 22), Interval(25, 31), Interval(35, 39), Interval(36, 39)]
        
        nclist = ncl.NestedContainmentList(self.fname, ivls)
        
        self.assertEquals(nclist.root.variables['ivls'][:].tolist(), [[0, 10, -1], [2, 30, 1], [25, 31, -1], [35, 39, 4], [3, 20, 2], [20, 25, 3], [5, 7, -1], [9, 15, -1], [21, 22, -1], [36, 39, -1]])
        self.assertEquals(nclist.root.variables['grps'][:].tolist(), [[0, 4], [4, 2], [6, 2], [8, 1], [9, 1]])
        nclist.close()
    
    def test_intersect(self):
        ivls = [Interval(0, 10), Interval(2, 30), Interval(3, 20), Interval(5, 7), Interval(9, 15), Interval(20, 25),
                Interval(21, 22), Interval(25, 31), Interval(35, 39), Interval(36, 39)]
        
        nclist = ncl.NestedContainmentList(self.fname, ivls)
        
        self.assertEquals({Interval(2, 30), Interval(3, 20), Interval(20, 25), Interval(21, 22), Interval(25, 31)},
                          set(nclist.intersect(Interval(15, 30))))
        nclist.close()

if __name__ == "__main__":
    import sys
    sys.exit(unittest.main())