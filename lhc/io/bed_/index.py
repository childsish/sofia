from iterator import BedLineIterator


class IndexedBedFile(object):
    def __init__(self, index):
        self.index = index

    def fetch(self, chr, start, stop=None):
        if stop is None:
            stop = start + 1
        return [BedLineIterator.parse_line(line) for line in self.index.fetch(chr, start, stop)]
