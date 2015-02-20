from iterator import GtfEntryIterator


class IndexedGtfFile(object):
    def __init__(self, index):
        self.index = index

    def fetch(self, chr, start, stop):
        return GtfEntryIterator.get_features(self.index.fetch(chr, start, stop))
