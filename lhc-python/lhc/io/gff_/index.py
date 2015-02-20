from iterator import GffEntryIterator


class IndexedGffFile(object):
    def __init__(self, index):
        self.index = index

    def fetch(self, chr, start, stop):
        return GffEntryIterator.get_features(self.index.fetch(chr, start, stop))
