import sys

from lhc.file_format import gtf
from modules.parser import Parser

class GtfParser(Parser):
    
    EXT = '.gtf'
    
    def __init__(self, fname, iname=None):
        super(GtfParser, self).__init__(fname, iname)
        self.parser = gtf.GtfParser(fname, iname)
    
    def __iter__(self):
        return iter(self.parser)
    
    def __getitem__(self, key):
        try:
            return self.parser[key]
        except:
            sys.stderr.write('Missing chromosome: %s\n'%str(key.chr))
        return None
    
    def index(self, iname=None):
        gtf.index(self.fname, iname)

