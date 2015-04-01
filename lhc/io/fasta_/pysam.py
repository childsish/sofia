import pysam


class PysamFastaSet(object):
    def __init__(self, fname, extension='.fai'):
        self.index = pysam.FastaFile(fname + extension)

    def __getitem__(self, key):
        return PysamFastaEntry(self.index, key)

    def fetch(self, chr, start, stop):
        return self.index.fetch(chr, start, stop)


class PysamFastaEntry(object):
    def __init__(self, index, chr):
        self.index = index
        self.chr = chr

    def __str__(self):
        return self[:]

    def __getitem__(self, key):
        return self.index.fetch(self.chr, key, key + 1) if isinstance(key, int) else\
            self.index.fetch(self.chr, key.start, key.stop)

    def fetch(self, start, stop):
        return self.index.fetch(self.chr, start, stop)
