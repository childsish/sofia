from collections import namedtuple

KeyValuePair = namedtuple('KeyValuePair', ('key', 'value'))


class CompoundIndex(object):
    def __init__(self, index_classes, key=None):
        self.classes = index_classes
        self.index = self.classes[0]()
        self.type = 'inexact' if any(index.TYPE == 'inexact' for index in index_classes) else 'exact'
        self.return_ = 'multiple' if any(index.RETURN == 'multiple' for index in index_classes) else 'single'
        self.key = lambda x: x if key is None else key
    
    def __getitem__(self, key):
        if not isinstance(key, tuple) and len(self.classes) == 1:
            key = (key,)
        assert len(key) == len(self.classes)
        
        indices = [self.index]
        for i in xrange(len(self.classes)):
            next_indices = []
            for index in indices:
                if index.RETURN == 'single':
                    next_indices.append(index[key[i]])
                elif index.RETURN == 'multiple':
                    next_indices.extend(index[key[i]])
                else:
                    raise NotImplementedError('Can not handle indices with {} returns'.format(index.RETURN))
            indices = next_indices
        if self.type == 'exact':
            indices = [index.value for index in indices]
        if self.return_ == 'single':
            assert len(indices) == 1
            return indices[0]
        return indices
    
    def __setitem__(self, key, value):
        if not isinstance(key, tuple) and len(self.classes) == 1:
            key = (key,)
        stored_key = key[0] if len(self.classes) == 1 else key

        index = self.index
        for factory in self.classes[1:-1]:
            if key not in index:
                index[key] = factory.make()
            index = index[key]
        index[key] = KeyValuePair(stored_key, value)


class IndexFactory(object):

    RETURN = ''
    TYPE = ''
    
    def __contains__(self, key):
        raise NotImplementedError()
    
    def __getitem__(self, key):
        raise NotImplementedError()
    
    def __setitem__(self, key, value):
        raise NotImplementedError()
