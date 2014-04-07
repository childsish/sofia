class Index(object):
    def __init__(self, accessors):
        self.accessors = accessors
        self.index = self.accessors[0]()
    
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
                    msg = 'Can not handle indices with %s returns'%index.RETURN
                    raise NotImplementedError(msg)
            indices = next_level
        return indices
    
    def __setitem__(self, key, value):
        if not isinstance(key, tuple) and len(self.accessors) == 1:
            key = (key,)
        stored_key = key[0] if len(self.accessors) == 1 else key
        
        indices = [self.index]
        for i, accessor in enumerate(self.accessors):
            next_level = []
            for index in indices:
                index[key[i]] = (stored_key, value)\
                    if accessor is self.accessors[-1]\
                    else self.accessors[i + 1]()
                next_level.append(index[key[i]])
            indices = next_level


class Accessor(object):
    
    RETURN = ''
    
    def __getitem__(self):
        raise NotImplementedError()
    
    def __setitem__(self, key, value):
        raise NotImplementedError()
