import random
import unittest

from itertools import izip
from sorted_dict import SortedDict


class SortedDictTest(unittest.TestCase):
    def test_dict(self):
        keys = list(set(random.randint(0, 1000) for i in xrange(100)))
        random.shuffle(keys)
        values = [random.random() for i in xrange(len(keys))]
        d = SortedDict((key, value) for key, value in izip(keys, values))

        self.assertEqual(sorted(keys), d.keys)
        self.assertEqual([v for (k, v) in sorted(zip(keys, values))], d.values)
