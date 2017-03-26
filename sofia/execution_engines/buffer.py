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
        return len(self.items[self.keys.index(key)]) < self.n

    def read(self):
        return self.items

    def write(self, key, values):
        self.items[self.keys.index(key)].extend(values)
