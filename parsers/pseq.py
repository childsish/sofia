from lhc.file_format import pseq
from ebias.parser import Parser

class PseqParser(Parser):
    
    EXT = 'pseq'
    
    def __init__(self, fname, iname=None):
        super(PseqParser, self).__init__(fname, iname)
        self.parser = pseq.PseqParser(fname, iname)
    
    def __iter__(self):
        return iter(self.parser)
    
    def __getitem__(self, key):
        try:
            return self.parser[key]
        except KeyError:
            pass
        return None
    
    def index(self, iname=None):
        pseq.index(self.fname, iname)
