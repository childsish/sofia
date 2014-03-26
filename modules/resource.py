from modules.feature import Feature

class Resource(object):
    
    NAME = ''
    
    def __init__(self, fname, iname=None):
        self.fname = fname
        self.iname = iname
    
    def __iter__(self):
        msg = 'This resource can not be used as the query resource'
        raise NotImplementedError(msg)
    
    def __getitem__(self, entities):
        msg = 'This resource can not be used as a target resource'
        raise NotImplementedError(msg)

    def index(self, iname):
        msg = 'This resource can not be indexed'
        raise NotImplementedError(msg)
