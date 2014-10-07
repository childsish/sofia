from collections import defaultdict
from operator import or_

class IdMap(object):
    """ An map for equivalent ids.

    Will create a map from one column of a tab delimited file to another.
    Always requires a header line.
    """
    def __init__(self, fname, fr=None, to=None, id_map=None):
        fhndl = open(fname)
        hdrs = fhndl.next().strip().split('\t')
        fr_idx = 0 if fr is None else hdrs.index(fr)
        to_idx = 1 if to is None else hdrs.index(to)
        self.map = defaultdict(set)
        for line in fhndl:
            parts = line.strip().split('\t')
            try:
                self.map[parts[fr_idx]].add(parts[to_idx])
            except IndexError:
                pass
        fhndl.close()
        self.id_map = id_map
    
    def __getitem__(self, key):
        if self.id_map is not None:
            key = self.id_map[key]
        if isinstance(key, basestring):
            return self.map[key]
        res = reduce(or_, (self.map[k] for k in key), set())
        if len(res) == 1:
            return list(res)[0]
        return list(res)
