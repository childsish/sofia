class KmerCounter(object):
    def __init__(self, sequence, k=None):
        self.sequence = sequence
        self.counts = {}
        if k is not None:
            self._count_k(k)

    def __getitem__(self, key):
        if key in self.counts:
            return self.counts[key]
        self._count_k(len(key))

    def _count_k(self, k):
        for i in xrange(0, len(self.sequence)):
            kmer = self.sequence[i:i + k]
            if kmer not in self.counts:
                self.counts[kmer] = 0
            self.count[kmer] += 1
