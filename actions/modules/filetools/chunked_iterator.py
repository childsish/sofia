import itertools


class ChunkedIterator(object):
    def __init__(self, fhndl, chunk):
        self.fhndl = fhndl
        self.chunk = chunk
        self.zip = chunk * (self.fhndl,)

    def __iter__(self):
        for lines in itertools.izip_longest(self.zip):
            yield lines
