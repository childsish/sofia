class IndexedFastaSet(object):
    def __init__(self, index):
        self.index = index

    def __getitem__(self, key):
        return IndexedFastaEntry(self.index, key)

    def fetch(self, chr, start, stop=None):
        if stop is None:
            stop = start + 1
        return self.index.fetch(chr, start, stop)


class IndexedFastaEntry(object):
    def __init__(self, index, chr):
        self.index = index
        self.chr = chr

    def __str__(self):
        return self[:]

    def __getitem__(self, key):
        return self.index.fetch(self.chr, key, key + 1) if isinstance(key, int) else\
            self.index.fetch(self.chr, key.start, key.stop)

    def fetch(self, start, stop=None):
        if stop is None:
            start = stop + 1
        return self.index.fetch(self.chr, start, stop)
