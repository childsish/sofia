import gzip

from index import Accessor

class FastaIndex(Accessor):
    
    __slots__ = ('chrs',)
    
    RETURN = 'single'
    TYPE = 'exact'
    
    def __init__(self, fname):
        self.chrs = {}
        infile = gzip.open(fname, 'rb') if fname.endswith('.gz') else\
            open(fname, 'rU')
        for line in infile:
            if line[0] not in '#>':
                self.wrap = len(line.strip())
                self.newlines = line[self.wrap:]
                break
        infile.close()
    
    def __contains__(self, key):
        return key.chr in self.chrs
    
    def __getitem__(self, key):
        return self.chrs[key.chr] + key.pos + (key.pos / self.wrap) * len(self.newlines)
    
    def __setitem__(self, key, value):
        self.chrs[key] = value


    def __getstate__(self):
        return dict((attr, getattr(self, attr)) for attr in self.__slots__)

    def __setstate_(self, state):
        for attr in self.__slots__:
            setattr(self, state[attr])

