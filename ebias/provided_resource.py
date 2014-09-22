import os

class ProvidedResource(object):
    def __init__(self, fname, type, name=None, init_args={}):
        self.fname = fname
        self.type = type
        self.name = os.path.basename(fname) if name is None else name
        self.init_args = init_args

    def __str__(self):
        return '%s;type=%s;%s'%(self.fname, self.type, self.name)
