from collections import Counter


class Skew(object):
    def __init__(self, sequence):
        self.counts = Counter(sequence.lower())

    def __str__(self):
        return str(self.counts)

    def __getitem__(self, key):
        if len(key) != 2:
            raise KeyError('invalid skew')
        x = self.counts[key[0].lower()]
        y = self.counts[key[1].lower()]
        if x + y == 0:
            return 0
        return (x - y) / float(x + y)
