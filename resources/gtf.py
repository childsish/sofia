from lhc.file_format import gtf
from modules.resource import Resource

class GtfParser(Resource):
    
    NAME = 'gtf'
    
    def __init__(self, fname, iname=None):
        super(GtfParser, self).__int__(fname, iname)
        self.parser = gtf.GtfParser(fname, iname)
    
    def __iter__(self):
        return iter(self.parser)
    
    def __getitem__(self, key):
        return self.parser[key]
    
    def index(self, iname=None):
        gtf.index(self.fname, iname)
