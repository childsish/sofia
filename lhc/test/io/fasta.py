import os
import tempfile
import unittest

from subprocess import Popen

from lhc.binf.genomic_coordinate import Position, Interval
from lhc.io.fasta_.iterator import FastaEntryIterator
from lhc.io.fasta_.set_ import FastaSet
from lhc.io.fasta_.index import IndexedFastaFile

class TestFasta(unittest.TestCase):
    
    def setUp(self):
        fhndl, self.fname = tempfile.mkstemp()
        os.write(fhndl, '>a x\naaaaaaaaaa\nbbbbbbbbbb\ncccccccccc\ndddddddddd\neeeeeeeeee\n>b y\nffffffffff\ngggggggggg\nhhhhh')
        os.close(fhndl)

        prc = Popen(['samtools', 'faidx', '%s'%self.fname])
        prc.wait()
    
    def test_iterEntries(self):
        it = FastaEntryIterator(self.fname)
        
        self.assertEquals(tuple(it.next()), ('a', 'aaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeee'))
        self.assertEquals(tuple(it.next()), ('b', 'ffffffffffgggggggggghhhhh'))
        self.assertRaises(StopIteration, it.next)
    
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

    def test_getItemIndexedByKey(self):
        parser = IndexedFastaFile(self.fname)
        
        self.assertEquals(str(parser['a']), 'aaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeee')
        self.assertEquals(str(parser['b']), 'ffffffffffgggggggggghhhhh')
    
    def test_getItemIndexedSinglePosition(self):
        parser = IndexedFastaFile(self.fname)
        
        self.assertEquals(parser[Position('a', 10)], 'b')
        self.assertEquals(parser[Position('b', 10)], 'g')
    
    def test_getItemIndexedInterval(self):
        parser = IndexedFastaFile(self.fname)
        
        self.assertEquals(parser[Interval('a', 10, 20)], 'bbbbbbbbbb')
        self.assertEquals(parser[Interval('b', 10, 20)], 'gggggggggg')
        self.assertEquals(parser[Interval('a', 5, 15)], 'aaaaabbbbb')
        self.assertEquals(parser[Interval('b', 5, 15)], 'fffffggggg')

    def tearDown(self):
        os.remove(self.fname)
        os.remove('%s.fai'%self.fname)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())

