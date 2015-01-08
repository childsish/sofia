import itertools


class ChunkedIterator(object):
    def __init__(self, it, chunk):
        self.zip = chunk * (it,)

    def __iter__(self):
        for lines in itertools.izip_longest(*self.zip):
            yield lines
