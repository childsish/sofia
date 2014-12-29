import os


class ProvidedResource(object):
    """ A resource that the user has provided. """
    def __init__(self, fname, type, name=None, param=None, attr=None):
        if not os.path.exists(fname):
            raise OSError('{} does not exist'.format(fname))
        self.fname = fname
        self.type = type
        self.name = os.path.basename(fname) if name is None else name
        self.param = {} if param is None else param
        self.attr = {} if attr is None else attr

    def __str__(self):
        return '{}:{}:{}'.format(self.fname, self.type, self.name)
