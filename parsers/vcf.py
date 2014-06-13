from lhc.file_format import vcf
from modules.parser import Parser

class VcfParser(Parser):
    
    EXT = '.vcf'
    IN = []
    OUT = ['genomic_position', 'variant']
    
    def __init__(self, fname, iname=None):
        super(VcfParser, self).__init__(fname, iname)
        self.parser = vcf.VcfParser(fname, iname)
    
    def __iter__(self):
        return iter(self.parser)
    
    def __getitem__(self, key):
        try:
            return self.parser[key]
        except KeyError:
            pass
        return None
    
    def index(self, iname=None):
        vcf.index(self.fname, iname)
