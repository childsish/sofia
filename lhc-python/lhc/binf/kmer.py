class KmerCounter(object):
    def __init__(self, sequence, k=None, step=1):
        self.sequence = sequence
        self.counts = {}
        self.step = step
        if k is not None:
            self._count_k(k)

    def __str__(self):
        return str(self.counts)

    def __getitem__(self, key):
        if key not in self.counts:
            self._count_k(len(key))
        return self.counts[key]

    def _count_k(self, k):
        for i in xrange(0, len(self.sequence), self.step):
            kmer = self.sequence[i:i + k]
            if kmer not in self.counts:
                self.counts[kmer] = 0
            self.counts[kmer] += 1
