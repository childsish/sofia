class Parser(object):
    
    EXT = ''
    
    def __init__(self, fname, iname=None):
        self.fname = fname
        self.iname = '%s.idx'%fname if iname is None else iname
    
    def __iter__(self):
        raise NotImplementedError()
    
    def __getitem__(self, key):
        raise NotImplementedError()
    
    def index(self, iname=None):
        raise NotImplementedError()
