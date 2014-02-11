import numpy as np

from bisect import bisect_left
from collections import Counter
from netCDF4 import Dataset
from tempfile import mkstemp

class NestedContainmentList(object):
    def __init__(self, root, ivls=None):
        mode = 'r' if ivls is None else 'w'
        self.root = Dataset(root, mode) if isinstance(root, basestring) else root
        self.closed = False
        if mode == 'w':
            parent_ids = self._getParentIds(ivls)
            grp_table, pnt2grp = self._getGroupTable(parent_ids)
            ivl_table = self._getIntervalTable(ivls, pnt2grp, parent_ids)
            self._populateRoot(ivl_table, grp_table)
    
    def intersect(self, ivl):
        grp_var = self.root.variables['grps']
        ivl_var = self.root.variables['ivls']
        res = []
        
        stk = [0]
        while len(stk) > 0:
            grp_fr, grp_sz = grp_var[stk.pop(0), :]
            grp_to = grp_fr + grp_sz
            grp_to = grp_fr + bisect_left(ivl_var[grp_fr:grp_to,0], ivl.stop)
            while grp_fr < grp_to:
                start, stop, grp_idx = ivl_var[grp_fr]
                if ivl.start < stop:
                    res.append(slice(start, stop))
                if grp_idx != -1:
                    stk.append(grp_idx)
                grp_fr += 1
        return res
    
    def close(self):
        if hasattr(self, 'closed') and not self.closed and hasattr(self.root, 'closed'):
            self.root.close()
    
    def _getParentIds(self, ivls):
        parent_ids = -1 * np.ones(len(ivls), dtype='i4')
        
        ivls.sort()
        i = 0
        while i < len(ivls):
            parent = i
            i += 1
            while i < len(ivls) and parent >= 0:
                if ivls[i].stop > ivls[parent].stop or ivls[i] == ivls[parent]:
                    parent = parent_ids[parent]
                else:
                    parent_ids[i] = parent
                    parent = i
                    i += 1
        return parent_ids
    
    def _getGroupTable(self, parent_ids):
        cnts = Counter(parent_ids)
        pnt2grp = {}
        grp_table = np.empty((len(cnts), 2), dtype='i4')
        
        cpos = 0
        for group_id, (parent_id, group_size) in enumerate(sorted(cnts.iteritems())):
            pnt2grp[parent_id] = group_id
            grp_table[group_id,0] = cpos
            grp_table[group_id,1] = group_size
            cpos += group_size
        del pnt2grp[-1]
        return grp_table, pnt2grp
    
    def _getIntervalTable(self, ivls, pnt2grp, parent_ids):
        ivl_table = np.array([[ivl.start, ivl.stop, -1] for ivl in ivls], dtype='i4')
        for pnt_id, grp_id in pnt2grp.iteritems():
            ivl_table[pnt_id,2] = grp_id
        idxs = np.argsort(parent_ids)
        ivl_table = ivl_table[idxs]
        return ivl_table
    
    def _populateRoot(self, ivl_table, grp_table):
        self.root.createDimension('ivls', len(ivl_table))
        self.root.createDimension('ivl_col', 3)
        self.root.createDimension('grps', len(grp_table))
        self.root.createDimension('grp_col', 2)
        self.root.createVariable('ivls', 'i4', ('ivls', 'ivl_col'))[:] = ivl_table
        self.root.createVariable('grps', 'i4', ('grps', 'grp_col'))[:] = grp_table
