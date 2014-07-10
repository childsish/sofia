class Resource(object):
    def __init__(self, fname, type, name=None):
        self.fname = fname
        self.type = type
        self.name = fname if name is None else name
