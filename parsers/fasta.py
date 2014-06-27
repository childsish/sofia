from lhc.file_format import fasta
from ebias.parser import Parser

class FastaParser(Parser):
    
    EXT = 'fasta'
    
    def __init__(self, fname, iname=None):
        super(FastaParser, self).__init__(fname, iname)
        self.parser = fasta.FastaParser(fname, iname)
    
    def __iter__(self):
        return iter(self.parser)
    
    def __getitem__(self, key):
        return self.parser[key]
    
    def index(self, iname=None):
        fasta.index(self.fname, iname)
