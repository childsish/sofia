import gzip

class EntrySet(object):
    
    EXT = '.idx'
    
    def __iter__(self):
        infile = gzip.open(self.fname) if self.fname.endswith('.gz')\
            else open(self.fname)
        for entry in self._iterHandle(infile):
            yield entry
        infile.close()
    
    @classmethod
    def getIndexName(cls, fname):
        return '%s%s'%(fname, cls.EXT)
    
    def _iterHandle(self, infile):
        raise NotImplementedError()
