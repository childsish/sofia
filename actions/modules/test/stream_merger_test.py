import random
import string
import unittest


from sorted_iterator_merger import SortedIteratorMerger


class StreamMergerTest(unittest.TestCase):
    def setUp(self):
        full_stream = list(string.letters)
        random.shuffle(full_stream)
        splits = [0] + sorted({random.randint(1, len(full_stream)) for i in xrange(4)}) + [len(full_stream)]
        self.lists = [full_stream[fr:to] for fr, to in zip(splits[:-1], splits[1:])]

    def test_merger(self):
        iterators = [iter(sorted(l)) for l in self.lists]
        it = SortedIteratorMerger(iterators)

        self.assertEqual(sorted(string.letters), list(it))

    def test_key(self):
        key = lambda x: ord('z') - ord(x)
        iterators = [iter(sorted(l, key=key)) for l in self.lists]
        it = SortedIteratorMerger(iterators, key=key)

        self.assertEqual(sorted(string.letters)[::-1], list(it))
