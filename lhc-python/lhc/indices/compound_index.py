from collections import namedtuple

KeyValuePair = namedtuple('KeyValuePair', ('key', 'value'))


class CompoundIndex(object):
    def __init__(self, *index_classes, **kwargs):
        self.classes = index_classes
        self.index = self.classes[0]()
        self.type = 'inexact' if any(index.TYPE == 'inexact' for index in index_classes) else 'exact'
        self.return_ = 'multiple' if any(index.RETURN == 'multiple' for index in index_classes) else 'single'
        self.key = kwargs['key'] if 'key' in kwargs else (lambda x: x)

    def __contains__(self, key):
        key = self.key(key)
        index = self.index
        for i in xrange(len(self.factories) - 2):
            if key not in index:
                return False
            index = index[key]
        return key in index
    
    def __getitem__(self, key):
        key = self.key(key)
        indices = [self.index]
        for key_part in key:
            next_indices = []
            for index in indices:
                if index.RETURN == 'single':
                    next_indices.append(index[key_part])
                elif index.RETURN == 'multiple':
                    next_indices.extend(index[key_part])
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
        used_key = self.key(key)
        index = self.index
        for key_part, index_class in zip(used_key[:-1], self.classes[1:]):
            if key_part not in index:
                index[key_part] = index_class()
            index = index[key_part]
        index[used_key[-1]] = KeyValuePair(key, value)
