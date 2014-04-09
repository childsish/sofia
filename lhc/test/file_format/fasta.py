import os
import tempfile
import unittest

from lhc.binf.genomic_coordinate import Position, Interval
from lhc.file_format import fasta

class TestFasta(unittest.TestCase):
    
    def setUp(self):
        fhndl, self.fname = tempfile.mkstemp()
        os.write(fhndl, '>a x\naaaaaaaaaa\nbbbbbbbbbb\ncccccccccc\ndddddddddd\neeeeeeeeee\n>b y\nffffffffff\ngggggggggg\nhhhhh')
        os.close(fhndl)
    
    def test_iterEntries(self):
        it = fasta.iterEntries(self.fname)
        
        self.assertEquals(tuple(it.next()), ('a', 'aaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeee'))
        self.assertEquals(tuple(it.next()), ('b', 'ffffffffffgggggggggghhhhh'))
        self.assertRaises(StopIteration, it.next)
    
    def test_getItemByKey(self):
        parser = fasta.FastaParser(self.fname)
        
        self.assertEquals(parser['a'], 'aaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeee')
        self.assertEquals(parser['b'], 'ffffffffffgggggggggghhhhh')
    
    def test_getItemSinglePosition(self):
        parser = fasta.FastaParser(self.fname)
        
        self.assertEquals(parser[Position('a', 10)], 'b')
        self.assertEquals(parser[Position('b', 10)], 'g')
    
    def test_getItemInterval(self):
        parser = fasta.FastaParser(self.fname)
        
        self.assertEquals(parser[Interval('a', 10, 20)], 'bbbbbbbbbb')
        self.assertEquals(parser[Interval('b', 10, 20)], 'gggggggggg')
        self.assertEquals(parser[Interval('a', 5, 15)], 'aaaaabbbbb')
        self.assertEquals(parser[Interval('b', 5, 15)], 'fffffggggg')

    def test_getItemIndexedByKey(self):
        fasta.index(self.fname)
        parser = fasta.FastaParser(self.fname)
        
        self.assertEquals(parser['a'], 'aaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeee')
        self.assertEquals(parser['b'], 'ffffffffffgggggggggghhhhh')
    
    def test_getItemIndexedSinglePosition(self):
        fasta.index(self.fname)
        parser = fasta.FastaParser(self.fname)
        
        self.assertEquals(parser[Position('a', 10)], 'b')
        self.assertEquals(parser[Position('b', 10)], 'g')
    
    def test_getItemIndexedInterval(self):
        fasta.index(self.fname)
        parser = fasta.FastaParser(self.fname)
        
        self.assertEquals(parser[Interval('a', 10, 20)], 'bbbbbbbbbb')
        self.assertEquals(parser[Interval('b', 10, 20)], 'gggggggggg')
        self.assertEquals(parser[Interval('a', 5, 15)], 'aaaaabbbbb')
        self.assertEquals(parser[Interval('b', 5, 15)], 'fffffggggg')

    def tearDown(self):
        os.remove(self.fname)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())

