import os


class ProvidedResource(object):
    """ A resource that the user has provided. """
    def __init__(self, fname, format=None, name=None, attr=None, ins=None, outs=None):
        if not os.path.exists(fname):
            raise OSError('{} does not exist'.format(fname))
        self.fname = fname
        self.format = format
        self.name = os.path.basename(fname) if name is None else name
        self.attr = {} if attr is None else attr
        self.attr['resource'] = self.name
        self.ins = ins
        self.outs = outs

    def __str__(self):
        return '{}:{}'.format(self.fname, self.name)
