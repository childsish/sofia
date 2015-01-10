import itertools

from index import Accessor

class FastaIndex(Accessor):
    
    __slots__ = ('chrs', 'wrap', 'newlines')
    
    RETURN = 'single'
    TYPE = 'exact'
    
    def __init__(self, fname):
        self.chrs = {}
        infile = open(fname, 'rU')
        for line in infile:
            if line[0] not in '#>':
                self.wrap = len(line.strip())
                self.newlines = line[self.wrap:]
                break
        infile.close()
    
    def __contains__(self, key):
        key = key.chr if hasattr(key, 'chr') else key
        return key in self.chrs
    
    def __getitem__(self, key):
        chr = key.chr if hasattr(key, 'chr') else key
        pos = key.pos if hasattr(key, 'chr') else 0
        return self.chrs[chr] + pos + (pos / self.wrap) * len(self.newlines)
    
    def __setitem__(self, key, value):
        self.chrs[key] = value


    def __getstate__(self):
        return dict((attr, getattr(self, attr)) for attr in self.__slots__)

    def __setstate__(self, state):
        for attr in self.__slots__:
            setattr(self, attr, state[attr])

