import json

from modules.resource import Resource

class JsonParser(Resource):
    
    NAME = 'gtf'
    
    def __init__(self, fname, iname=None):
        super(JsonParser, self).__int__(fname, iname)
        self.data = json.load(fname)
    
    def __getitem__(self, key):
        return self.data[key]
