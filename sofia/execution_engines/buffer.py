class Buffer(object):
    def __init__(self, keys, n=None):
        self.keys = keys
        self.n = n
        self.items = [[] for key in keys]

    def __contains__(self, item):
        return item in self.keys

    def is_readable(self):
        return all(len(input) > 0 for input in self.items)

    def is_writable(self, key):
        if key not in self.keys:
            raise ValueError('Key mismatched. Please check that all attributes match.')
        return len(self.items[self.keys.index(key)]) < self.n

    def read(self):
        return self.items

    def write(self, key, values):
        for i, k in enumerate(self.keys):
            if key == k:
                self.items[i].extend(values)
