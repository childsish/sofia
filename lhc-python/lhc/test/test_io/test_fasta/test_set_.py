import unittest

from lhc.binf.genomic_coordinate import GenomicPosition as Position, GenomicInterval as Interval
from lhc.io.fasta_.iterator import FastaEntryIterator
from lhc.io.fasta_.set_ import FastaSet


class TestFasta(unittest.TestCase):
    def setUp(self):
        self.lines = ['>a x\n',
                      'aaaaaaaaaa\n',
                      'bbbbbbbbbb\n',
                      'cccccccccc\n',
                      'dddddddddd\n',
                      'eeeeeeeeee\n',
                      '>b y\n',
                      'ffffffffff\n',
                      'gggggggggg\n',
                      'hhhhh\n']

    def test_getItemByKey(self):
        parser = FastaSet(FastaEntryIterator(iter(self.lines)))

        self.assertEquals(parser['a'], 'aaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeee')
        self.assertEquals(parser['b'], 'ffffffffffgggggggggghhhhh')

    def test_getItemSinglePosition(self):
        parser = FastaSet(FastaEntryIterator(iter(self.lines)))

        self.assertEquals(parser[Position('a', 10)], 'b')
        self.assertEquals(parser[Position('b', 10)], 'g')

    def test_getItemInterval(self):
        parser = FastaSet(FastaEntryIterator(iter(self.lines)))

        self.assertEquals(parser[Interval('a', 10, 20)], 'bbbbbbbbbb')
        self.assertEquals(parser[Interval('b', 10, 20)], 'gggggggggg')
        self.assertEquals(parser[Interval('a', 5, 15)], 'aaaaabbbbb')
        self.assertEquals(parser[Interval('b', 5, 15)], 'fffffggggg')

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
