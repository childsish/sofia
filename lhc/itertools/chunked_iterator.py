from itertools import islice


class ChunkedIterator(object):
    def __init__(self, iterator, chunk):
        self.iterator = iterator
        self.chunk = chunk

    def __iter__(self):
        return self

    def next(self):
        return islice(self.iterator, 0, self.chunk)
