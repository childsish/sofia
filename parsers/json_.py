import json

from ebias.parser import Parser

class JsonParser(Parser):
    
    EXT = 'json'
    
    def __init__(self, fname, iname=None):
        super(JsonParser, self).__init__(fname, iname)
        infile = open(fname)
        self.data = json.load(infile)
        infile.close()
    
    def __getitem__(self, key):
        return self.data[key]
