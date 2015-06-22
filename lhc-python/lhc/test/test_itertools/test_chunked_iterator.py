import itertools
import random
import string
import unittest

from lhc.itertools import ChunkedIterator


class TestChunkedIterator(unittest.TestCase):
    def test_chunked_iterator(self):
        x = [random.sample(string.letters, 1)[0] for i in itertools.repeat(None, 20)]
        it = ChunkedIterator(x, 6)

        self.assertEquals(it.next(), tuple(x[:6]))
        self.assertEquals(it.next(), tuple(x[6:12]))
        self.assertEquals(it.next(), tuple(x[12:18]))
        self.assertEquals(it.next(), tuple(x[18:]))


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())