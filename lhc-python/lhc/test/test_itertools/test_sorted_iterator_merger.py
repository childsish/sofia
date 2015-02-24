import random
import string
import unittest


from lhc.itertools import SortedIteratorMerger


class SortedIteratorMergerTest(unittest.TestCase):
    def setUp(self):
        self.full_stream = 'JfVmmCQlaFdeQcKgAuPfxhLsunJgKCHoAmAbGaYekeLWHXmwCSGqmfeTWNGKWPDnnbgusGWLlhKvwjxo'
        splits = [0] + sorted({random.randint(1, len(self.full_stream)) for i in xrange(4)}) + [len(self.full_stream)]
        self.lists = [self.full_stream[fr:to] for fr, to in zip(splits[:-1], splits[1:])]

    def test_merger(self):
        iterators = [iter(sorted(l)) for l in self.lists]
        it = SortedIteratorMerger(iterators)

        self.assertEqual(sorted(self.full_stream), list(it))

    def test_key(self):
        key = lambda x: ord('z') - ord(x)
        iterators = [iter(sorted(l, key=key)) for l in self.lists]
        it = SortedIteratorMerger(iterators, key=key)

        self.assertEqual(sorted(self.full_stream)[::-1], list(it))
