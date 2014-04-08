class EntrySet(object):
    
    EXT = '.idx'
    
    @classmethod
    def getIndexName(cls, fname):
        return '%s%s'%(fname, cls.EXT)
