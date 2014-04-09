from index import Accessor

class FastaIndex(Accessor):
    
    RETURN = 'single'
    
    def __init__(self, fname):
        self.chrs = {}
        infile = open(fname, 'rU')
        for line in infile:
            if line[0] not in '#>':
                self.wrap = len(line.strip())
                break
        self.newlines = infile.newlines
        infile.close()
    
    def __contains__(self, key):
        return key.chr in self.chrs
    
    def __getitem__(self, key):
        return self.chrs[key.chr] + key.pos + (key.pos / self.wrap) * len(self.newlines)
    
    def __setitem__(self, key, value):
        self.chrs[key] = value
