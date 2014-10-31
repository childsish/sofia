from itertools import izip

class IdMap(object):
    """ An map for equivalent ids.

    Will create a map from one column of a tab delimited file to another.
    Always requires a header line.
    """
    def __init__(self, fname):
        fhndl = open(fname)
        self.hdrs = fhndl.next().strip().split('\t')
        self.map = {}
        for line in fhndl:
            parts = line.strip().split('\t')
            for entry in izip(self.hdrs, parts):
                self.map[entry] = dict(izip(self.hdrs, parts))
        fhndl.close()
    
    def mapIdentifier(self, fr, to, key):
        return self.map[(fr, key)][to]
