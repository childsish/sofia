from iterator import VcfEntryIterator


class IndexedVcfFile(object):
    def __init__(self, index):
        self.index = index

    def fetch(self, chr, start, stop):
        return [VcfEntryIterator.parse_line(line) for line in self.index.fetch(chr, start, stop)]
