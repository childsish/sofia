import os

class ProvidedResource(object):
    """ A resource that the user has provided. """
    def __init__(self, fname, type, name=None, init_args={}):
        self.fname = fname
        self.type = type
        self.name = os.path.basename(fname) if name is None else name
        self.init_args = init_args
        self.attrs = {}

    def __str__(self):
        return '%s;type=%s;%s'%(self.fname, self.type, self.name)
