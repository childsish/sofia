from netCDF4 import Dataset
from itertools import izip

class Sequence(object):
    def __init__(self, sequence_id=None, var=''):
        self.id = sequence_id
        self.var = var

    def __len__(self):
        return len(self.var)

    def __getitem__(self, key):
        if isinstance(key, int):
            fr = key
            to = key + 1
        elif isinstance(key, slice):
            fr = key.start
            to = key.stop
        elif hasattr(key, '__iter__'):
            raise NotImplementedError()
        else:
            raise TypeError('Unrecognised position type: %s'%(type(key),))

        return ''.join(self.var[fr:to])

    def __add__(self, other):
        if isinstance(other, basestring) and self.id == None:
            return other
        raise NotImplementedError('Sequence addition not implemented for type: %s'%(type(other)))

class SequenceSet(object):
    def __init__(self, fname, mode='r'):
        self.root = Dataset(fname, mode)

    def __del__(self):
        self.close()

    def __len__(self):
        return len(self.root.variables)
    
    def __getitem__(self, key):
        if key not in self.root.variables:
            raise KeyError('Sequence name "%s" not found in database'%key)
        return Sequence(key, self.root.variables[key])
    
    def __setitem__(self, key, value):
        dim = self.root.createDimension(key, len(value))
        var = self.root.createVariable(key, '|S1', (key,))
        var[:] = list(value)
    
    def __iter__(self):
        return self.root.variables.iteritems()
    
    def __contains__(self, key):
        return key in self.root.variables
    
    def iteritems(self):
        for item in izip(self.iterkeys(), self.itervalues()):
            yield (k, Sequence(k, self.root.variables[k]))
    
    def iterkeys(self):
        for k in self.root.variables:
            yield k
    
    def itervalues(self):
        for k in self.root.variables:
            yield Sequence(k, self.root.variables[k])
        
    def close(self):
        if hasattr(self, 'closed') and not self.closed:
            self.root.close()
            self.closed = True
