from collections import namedtuple

KeyValuePair = namedtuple('KeyValuePair', ('key', 'value'))


class Index(object):

    __slots__ = ('accessors', 'index', 'type', 'return_')
    
    def __init__(self, accessors):
        self.accessors = accessors
        self.index = self.accessors[0]()
        self.type = 'inexact' if 'inexact' in\
            (accessor.TYPE for accessor in accessors) else 'exact'
        self.return_ = 'multiple' if 'multiple' in\
            (accessor.RETURN for accessor in accessors) else 'single'
    
    def __getitem__(self, key):
        if not isinstance(key, tuple) and len(self.accessors) == 1:
            key = (key,)
        assert len(key) == len(self.accessors)
        
        indices = [self.index]
        for i in xrange(len(self.accessors)):
            next_level = []
            for index in indices:
                if index.RETURN == 'single':
                    next_level.append(index[key[i]])
                elif index.RETURN == 'multiple':
                    next_level.extend(index[key[i]])
                else:
                    msg = 'Can not handle indices with {} returns'.format(index.RETURN)
                    raise NotImplementedError(msg)
            indices = next_level
        if self.type == 'exact':
            indices = [index.value for index in indices]
        if self.return_ == 'single':
            assert len(indices) == 1
            return indices[0]
        return indices
    
    def __setitem__(self, key, value):
        if not isinstance(key, tuple) and len(self.accessors) == 1:
            key = (key,)
        stored_key = key[0] if len(self.accessors) == 1 else key
        
        indices = [self.index]
        for i in xrange(len(self.accessors)):
            next_level = []
            for index in indices:
                if i + 1 == len(self.accessors):
                    index[key[i]] = KeyValuePair(stored_key, value)
                elif key[i] not in index:
                    index[key[i]] = self.accessors[i + 1]()
                next_level.append(index[key[i]])
            indices = next_level

    def __getstate__(self):
        return dict((attr, getattr(self, attr)) for attr in self.__slots__)
    
    def __setstate__(self, state):
        for attr in self.__slots__:
            setattr(self, attr, state[attr])


class Accessor(object):
    
    RETURN = ''
    
    def __contains__(self, key):
        raise NotImplementedError()
    
    def __getitem__(self, key):
        raise NotImplementedError()
    
    def __setitem__(self, key, value):
        raise NotImplementedError()
