import numpy as np

from bisect import bisect_left
from collections import Counter
from netCDF4 import Dataset
from lhc.misc.tools import argsort

class NestedContainmentList(object):
    def __init__(self, root, ivls=None):
        """Create a nested containment list with a netCDF backend
        
        :param root: either a filename or the Dataset object to work upon
        :type root: string or netCDF4.Dataset
        :param ivls: if provided will insert the given intervals into the database overriding anything already there
        :type ivls: list of interval
        """
        mode = 'r' if ivls is None else 'w'
        self.root = Dataset(root, mode) if isinstance(root, basestring) else root
        self.closed = False
        if mode == 'w':
            ivl_table, grp_table, ordering = getTables(ivls)
            self._populateRoot(ivl_table, grp_table)
    
    def getOverlapping(self, ivl, grp_id=0):
        """Find all overlapping intervals
        
        :param interval ivl: find intervals intersecting this interval
        :param integer grp_id: the group to begin looking in
        """
        grp_var = self.root.variables['grps']
        ivl_var = self.root.variables['ivls']
        res = []
        
        stk = [grp_id]
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
    
    def _populateRoot(self, ivl_table, grp_table):
        self.root.createDimension('ivls', len(ivl_table))
        self.root.createDimension('ivl_col', 3)
        self.root.createDimension('grps', len(grp_table))
        self.root.createDimension('grp_col', 2)
        self.root.createVariable('ivls', 'i4', ('ivls', 'ivl_col'))[:] = ivl_table
        self.root.createVariable('grps', 'i4', ('grps', 'grp_col'))[:] = grp_table

def getTables(ivls):
    """Compute the interval and group tables of a nested containment list.
    
    :param ivls: the intervals to be stored in the table. Intervals are any object with .start and .stop members
    :type ivls: iterable of intervals
    """
    ivls, idx0 = _reduceIntervals(ivls)
    ivls, idx1 = _sortIntervals(ivls)
    parent_ids = _getParentIdxs(ivls)
    grp_table, pnt2grp = _getGroupTable(parent_ids)
    ivl_table, idx2 = _getIntervalTable(ivls, pnt2grp, parent_ids)
    
    return ivl_table, grp_table, np.argsort(idx2)[np.argsort(idx1)[idx0]]

def _reduceIntervals(ivls):
    visited = {}
    reduced_ivls = []
    reduced_idxs = np.empty(len(ivls), dtype='i4')
    for i, ivl in enumerate(ivls):
        key = (ivl.start, ivl.stop)
        if key not in visited:
            visited[key] = len(visited)
            reduced_ivls.append(ivl)
        reduced_idxs[i] = visited[key]
    return reduced_ivls, reduced_idxs 

def _sortIntervals(ivls):
    def cmp(x, y):
        if x.start < y.start:
            return -1
        elif x.start > y.start:
            return 1
        elif x.stop > y.stop:
            return -1
        return 1
    
    sorted_idxs = np.array(argsort(ivls, cmp=cmp), dtype='i4')
    sorted_ivls = [ivls[idx] for idx in sorted_idxs]
    return sorted_ivls, sorted_idxs

def _getParentIdxs(ivls):
    """Get the parent ids of the given intervals
    """
    parent_idxs = -1 * np.ones(len(ivls), dtype='i4')
    i = 0
    while i < len(ivls):
        parent = i
        i += 1
        while i < len(ivls) and parent >= 0:
            if ivls[i].stop > ivls[parent].stop or ivls[i] == ivls[parent]:
                parent = parent_idxs[parent]
            else:
                parent_idxs[i] = parent
                parent = i
                i += 1
    return parent_idxs
    
def _getGroupTable(parent_ids):
    pnt2grp = {}
    cnts = Counter(parent_ids)
    grp_table = np.empty((len(cnts), 2), dtype='i4')
    
    cpos = 0
    for group_id, (parent_id, group_size) in enumerate(sorted(cnts.iteritems())):
        pnt2grp[parent_id] = group_id
        grp_table[group_id,0] = cpos
        grp_table[group_id,1] = group_size
        cpos += group_size
    return grp_table, pnt2grp

def _getIntervalTable(ivls, pnt2grp, parent_ids):
    ivl_table = np.array([[ivl.start, ivl.stop, -1] for ivl in ivls], dtype='i4')
    for pnt_id, grp_id in pnt2grp.iteritems():
        if pnt_id >= 0:
            ivl_table[pnt_id,2] = grp_id
    idxs = np.argsort(parent_ids)
    ivl_table = ivl_table[idxs]
    return ivl_table, idxs