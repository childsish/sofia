from netCDF4 import Dataset
from header import getSequenceId

class NetCDFSequence(object):
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

class NetCDFSequenceSet(object):
    def __init__(self, fname, mode='r'):
        self.root = Dataset(fname, mode)

    def __del__(self):
        self.close()

    def __len__(self):
        return len(self.root.variables)
    
    def __iter__(self):
        return self.root.variables.iteritems()
        
    def __getitem__(self, key):
        key_converted = getSequenceId(key)
        if key_converted not in self.root.variables:
            raise KeyError('Sequence name "%s" not found in database'%key)
        return NetCDFSequence(key_converted, self.root.variables[key_converted])
    
    def __setitem__(self, key, value):
        key_converted = getSequenceId(key)
        if key_converted in self.root.variables:
            raise ValueError('Sequence name "%s" has already been defined'%key)
        dim = self.root.createDimension(key_converted, len(value))
        var = self.root.createVariable(key_converted, '|S1', (key_converted,))
        var[:] = list(value)

    def close(self):
        if hasattr(self, 'closed') and not self.closed:
            self.root.close()
            self.closed = True
