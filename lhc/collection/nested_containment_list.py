import numpy as np

from collections import Counter
from netCDF4 import Dataset

class NestedContainmentList(object):

    def __init__(self, root, mode='r', diskless=False):
        self.root = root
        if isinstance(root, basestring):
            self.root = Dataset(root, mode, diskless=diskless)
    
    def __getitem__(self, key):
        if isinstance(key, int):
            ivl = self.root.variables['ivls'][key,:]
            return slice(ivl[0], -ivl[1])
    
    def insertIntervals(self, ivls):
        ivls = np.array([[ivl.start, -ivl.stop] for ivl in ivls], dtype='i4')
        ivl_table, grp_table, ivl_map = self.getIntervalTable(ivls)
        self.populateRoot(ivl_table, grp_table)
        return ivl_map
    
    def getIntervalTable(self, ivls):
        def contains(a, b):
            return a[0] <= b[0] and a[1] <= b[1]
        
        owner_ids = np.zeros(len(ivls), dtype='i4')
        member_ids = np.zeros(len(ivls), dtype='i4')
        
        idxs = np.lexsort((ivls[:,1], ivls[:,0]))
        sublist_id = 1
        stk = []
        for i in xrange(len(idxs) - 1):
            member_ids[i] = 0 if len(stk) == 0 else stk[-1][1]
            if contains(ivls[idxs[i]], ivls[idxs[i + 1]]):
                stk.append((ivls[idxs[i]], sublist_id))
                owner_ids[idxs[i]] = sublist_id
                sublist_id += 1
            while len(stk) > 0 and not contains(stk[-1][0], ivls[idxs[i + 1]]):
                stk.pop()
        member_ids[-1] = 0 if len(stk) == 0 else stk[-1][1]
        idxs = idxs[np.argsort(member_ids)]
        
        grp_table = self.getSubGroupTable(member_ids)
        return np.column_stack((ivls[idxs], owner_ids[idxs])), grp_table, np.argsort(idxs)
    
    def getSubGroupTable(self, member_ids):
        cnts = Counter(member_ids)
        grp_table = np.empty((len(cnts), 2), dtype='i4')
        ttl = 0
        for k, cnt in sorted(cnts.iteritems()):
            grp_table[k,] = np.array([ttl, cnt]) 
            ttl += cnt
        return grp_table
    
    def populateRoot(self, ivls, grps):
        self.root.createDimension('ivls', len(ivls))
        self.root.createDimension('ivl_col', 3)
        self.root.createDimension('grps', len(grps))
        self.root.createDimension('grp_col', 2)
        self.root.createVariable('ivls', 'i4', ('ivls', 'ivl_col'))[:] = ivls
        self.root.createVariable('grps', 'i4', ('grps', 'grp_col'))[:] = grps
