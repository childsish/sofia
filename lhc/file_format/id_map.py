class IdMap(object):
    def __init__(self, fname, fr, to):
        fhndl = open(fname)
        hdrs = fhndl.next().strip().split('\t')
        fr_idx = hdrs.index(fr)
        to_idx = hdrs.index(to)
        self.map = {parts[fr_idx]: parts[to_idx] for parts in\
            (line.strip().split('\t') for line in fhndl)}
        fhndl.close()
    
    def __getitem__(self, key):
        return self.map[key]
