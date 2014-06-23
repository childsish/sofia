import gzip

class EntrySet(object):
    
    EXT = '.idx'
    
    def __init__(self, fname, iname=None):
        self.fname = fname
        self.fhndl = gzip.open(self.fname) if fname.endswith('.gz') else open(self.fname)
        self.iname = self.getIndexName(fname) if iname is None else iname
        self.data = None
    
    def __del__(self):
        if hasattr(self, 'fhndl') and not self.fhndl.closed:
            self.fhndl.close()
    
    def __iter__(self):
        self.fhndl.seek(0)
        for entry in self._iterHandle(self.fhndl):
            yield entry
    
    @classmethod
    def getIndexName(cls, fname):
        return '%s%s'%(fname, cls.EXT)
    
    def _iterHandle(self, infile):
        raise NotImplementedError()
