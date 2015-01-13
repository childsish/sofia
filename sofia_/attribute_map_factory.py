class AttributeMapFactory(object):
    def __init__(self, fname):
        self.fname = fname

        fhndl = open(fname)
        self.hdrs = fhndl.readline().strip().split('\t')
        fhndl.close()

    def make(self, fr, to):
        fr_idx = self.hdrs.index(fr)
        to_idx = self.hdrs.index(to)
        fhndl = open(self.fname)
        fhndl.next()
        attribute_map = {parts[fr_idx].strip(): parts[to_idx].strip() for parts in (line.split('\t') for line in fhndl)}
        fhndl.close()
        return attribute_map
