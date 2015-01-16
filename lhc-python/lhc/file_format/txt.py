class TypedColumnExtractor(object):

    TYPES = {
        'i': int,
        's': str,
        'f': float
    }

    def __init__(self, iterator, columns=('s1',), sep='\t', types=None):
        self.iterator = iterator
        if types is None:
            types = self.TYPES
        self.columns = [(types[c[0]], int(c[1]) - 1) for c in columns]
        self.sep = sep

    def __iter__(self):
        sep = self.sep
        columns = self.columns
        for line in self.iterator:
            parts = line.split(sep)
            yield (t(parts[i]) for t, i in columns)
