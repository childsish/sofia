import os
import tempfile
import unittest

from lhc.binf.genomic_coordinate import GenomicPosition as Position, GenomicInterval as Interval
from lhc.io.fasta_.iterator import FastaEntryIterator
from lhc.io.fasta_.set_ import FastaSet


class TestFasta(unittest.TestCase):

    def setUp(self):
        fhndl, self.fname = tempfile.mkstemp()
        os.write(fhndl, '>a x\naaaaaaaaaa\nbbbbbbbbbb\ncccccccccc\ndddddddddd\neeeeeeeeee\n>b y\nffffffffff\ngggggggggg\nhhhhh')
        os.close(fhndl)

    def test_getItemByKey(self):
        parser = FastaSet(FastaEntryIterator(self.fname))

        self.assertEquals(parser['a'], 'aaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeee')
        self.assertEquals(parser['b'], 'ffffffffffgggggggggghhhhh')

    def test_getItemSinglePosition(self):
        parser = FastaSet(FastaEntryIterator(self.fname))

        self.assertEquals(parser[Position('a', 10)], 'b')
        self.assertEquals(parser[Position('b', 10)], 'g')

    def test_getItemInterval(self):
        parser = FastaSet(FastaEntryIterator(self.fname))

        self.assertEquals(parser[Interval('a', 10, 20)], 'bbbbbbbbbb')
        self.assertEquals(parser[Interval('b', 10, 20)], 'gggggggggg')
        self.assertEquals(parser[Interval('a', 5, 15)], 'aaaaabbbbb')
        self.assertEquals(parser[Interval('b', 5, 15)], 'fffffggggg')

    def tearDown(self):
        os.remove(self.fname)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())

