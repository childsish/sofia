import itertools


class ChunkedIterator(object):
    def __init__(self, iterator, chunk):
        zipped = chunk * (iterator,)
        self.iterator = itertools.izip_longest(*zipped)

    def __iter__(self):
        return self

    def next(self):
        return self.iterator.next()
