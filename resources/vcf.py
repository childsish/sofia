from lhc.file_format import vcf
from modules.resource import Resource

class VcfParser(Resource):
    
    NAME = 'vcf'
    
    def __init__(self, fname, iname=None):
        super(VcfParser, self).__int__(fname, iname)
        self.parser = vcf.VcfParser(fname, iname)
    
    def __iter__(self):
        return iter(self.parser)
    
    def __getitem__(self, key):
        return self.parser[key]
    
    def index(self, iname=None):
        vcf.index(self.fname, iname)
