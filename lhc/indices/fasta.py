from lhc.indices.index import Index


class FastaIndex(Index):
    
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
