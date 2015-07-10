class Set(object):
    def __init__(self, iterator, index_factory=None, key=None):
        self.index = index
        key = (lambda x: x) if key is None else key
        for entry in iterator:
            self.index[key(entry)] = entry

    def __getitem__(self, key):
        return [v for k, v in self.index[key]]
