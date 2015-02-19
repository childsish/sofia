import bisect
import itertools


class SortedValueDict(object):
    """
    A dictionary sorted on the values

    **Warning!** This container can be dangerous to use. As dictionary values can be mutable, the container wraps all
    returned values in a ValueWrapper, which in turn will wrap any accessed members. This allows the ValueWrapper to
    update the parent dict when the value changes, but in turn means that any value you get from the dictionary nor any
    of the values members, are not exactly what you expect. The ValueWrapper provides a function "get_value" that
    returns the original value.

    Be absolutely certain that you need this container before using it.
    """
    def __init__(self, iterator=None, key=None):
        self.key = (lambda x: x) if key is None else key
        if iterator is None:
            self.values = []
            self.index_to_key = []
        else:
            sorted_items = sorted(((v, k) for k, v in iterator), key=lambda item: self.key(item[0]))
            self.values, self.index_to_key = [list(r) for r in itertools.izip(*sorted_items)]
        self.keys = [self.key(v) for v in self.values]
        self.key_to_index = {k: i for i, k in enumerate(self.index_to_key)}

    def __str__(self):
        return '{%s}' % ', '.join(['%s:%s' % entry for entry in self.iteritems()])

    def __iter__(self):
        return iter(self.index_to_key)

    def __len__(self):
        return len(self.key_to_index)

    def __contains__(self, key):
        return key in self.key_to_index

    def __getitem__(self, key):
        return ValueWrapper(key, self.values[self.key_to_index[key]], self)

    def __setitem__(self, key, value):
        if key in self.key_to_index:
            idx = self.key_to_index[key]
            if cmp(self.values[idx], value) == 0:
                self.values[idx] = value
                return
            del self[key]
        idx = bisect.bisect_left(self.keys, self.key(value))
        self.key_to_index[key] = idx
        self.index_to_key.insert(idx, key)
        self.values.insert(idx, value)
        self.keys.insert(idx, self.key(value))

    def __delitem__(self, key):
        idx = self.key_to_index[key]
        del self.key_to_index[key]
        del self.index_to_key[idx]
        del self.values[idx]
        del self.keys[idx]

    def get(self, key, default):
        try:
            return ValueWrapper(key, self[key], self)
        except KeyError:
            pass
        return default

    def refresh(self, key):
        value = self[key].get_value()
        del self[key]
        self[key] = value

    def iterkeys(self):
        return iter(self.index_to_key)

    def itervalues(self):
        return iter(self.values)

    def iteritems(self):
        return itertools.izip(self.index_to_key, self.values)

    def pop_highest(self):
        key = self.index_to_key.pop()
        value = self.values.pop()
        del self.key_to_index[key]
        return key, value

    def pop_lowest(self):
        key = self.index_to_key.pop(0)
        value = self.values.pop(0)
        del self.key_to_index[key]
        self.key_to_index = {k: i for i, k in enumerate(self.index_to_key)}
        return key, value

    def peek_highest(self):
        return self.index_to_key[-1], self.values[-1]

    def peek_lowest(self):
        return self.index_to_key[0], self.values[0]


class ValueWrapper(object):
    def __init__(self, key, value, sorted_dict):
        super(ValueWrapper, self).__setattr__('key', key)
        super(ValueWrapper, self).__setattr__('value', value)
        super(ValueWrapper, self).__setattr__('sorted_dict', sorted_dict)

    def __call__(self, *args, **kwargs):
        res = self.value(*args, **kwargs)
        self.sorted_dict.refresh(self.key)
        return ValueWrapper(self.key, res, self.sorted_dict)

    def __getitem__(self, key):
        return ValueWrapper(self.key, self.value[key], self.sorted_dict)

    def __setitem__(self, key, value):
        old_value = self.value[key]
        self.value[key] = value
        if cmp(old_value, value) != 0:
            self.sorted_dict.refresh(self.key)

    def __getattr__(self, key):
        return ValueWrapper(self.key, getattr(self.value, key), self.sorted_dict)

    def __setattr__(self, key, value):
        old_value = getattr(self.value, key)
        setattr(self.value, key, value)
        if cmp(old_value, value) != 0:
            self.sorted_dict.refresh(self.key)

    def __eq__(self, other):
        return self.value == other

    def get_value(self):
        return self.value
