import os
import tempfile
import unittest

from StringIO import StringIO
from lhc.binf.genomic_coordinate import Position, Interval
from lhc.io.fasta_.index import IndexedFastaSet, FastaIndexer, index


class TestFasta(unittest.TestCase):
    
    def setUp(self):
        fhndl, self.fname = tempfile.mkstemp()
        os.write(fhndl, '>a x\naaaaaaaaaa\nbbbbbbbbbb\ncccccccccc\ndddddddddd\neeeeeeeeee\n>b y\nffffffffff\ngggggggggg\nhhhhh')
        os.close(fhndl)

        index(self.fname)

    def test_indexer(self):
        in_string = StringIO('>chr1\naaccggtt\naaccggtt\naa\n>chr2\naaacccgggtttt\naaacccgggtttt\na')
        indexer = FastaIndexer(in_string)

        self.assertEquals(('chr1', 18, 6, 8, 9), indexer.next())
        self.assertEquals(('chr2', 35, 33, 8, 9), indexer.next())
        self.assertRaises(StopIteration, indexer.next)
    
    def test_getItemIndexedByKey(self):
        parser = IndexedFastaSet(self.fname)
        
        self.assertEquals('aaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeee', str(parser['a']))
        self.assertEquals('ffffffffffgggggggggghhhhh', str(parser['b']))
    
    def test_getItemIndexedSinglePosition(self):
        parser = IndexedFastaSet(self.fname)
        
        self.assertEquals('b', parser.get_position('a', 10))
        self.assertEquals('g', parser.get_position('b', 10))
    
    def test_getItemIndexedInterval(self):
        parser = IndexedFastaSet(self.fname)
        
        self.assertEquals('bbbbbbbbbb', parser.get_interval('a', 10, 20))
        self.assertEquals('gggggggggg', parser.get_interval('b', 10, 20))
        self.assertEquals('aaaaabbbbb', parser.get_interval('a', 5, 15))
        self.assertEquals('fffffggggg', parser.get_interval('b', 5, 15))

    def tearDown(self):
        os.remove(self.fname)
        os.remove('{}.fai'.format(self.fname))

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
