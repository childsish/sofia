from iterator import MafLine


class IndexedMafFile(object):
    def __init__(self, fname, index):
        self.index = index

    def fetch(self, chr, start, stop):
        res = []
        for line in self.index.fetch(chr, start, stop):
            parts = line.rstrip('\r\n').split('\t')
            parts[5] = int(parts[5]) - 1
            parts[6] = int(parts[6])
            res.append(MafLine(*parts))
        return res
