from collections import Counter


class KmerCounter(object):
    def __init__(self, sequence, k=None, step=1):
        self.sequence = sequence.lower()
        self.counts = Counter()
        self.step = step
        self.ks = set()
        if k is not None:
            self.ks.add(k)
            self._count_k(k)

    def __str__(self):
        return str(self.counts)

    def __getitem__(self, key):
        if len(key) not in self.ks:
            self._count_k(len(key))
        return self.counts[key.lower()]

    def _count_k(self, k):
        for i in xrange(0, len(self.sequence), self.step):
            kmer = self.sequence[i:i + k]
            if kmer not in self.counts:
                self.counts[kmer] = 0
            self.counts[kmer] += 1
        self.ks.add(k)
