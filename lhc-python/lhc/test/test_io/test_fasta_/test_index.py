import os
import tempfile
import unittest

from lhc.io.fasta_.indexer import index
from lhc.io.fasta_.index import IndexedFastaSet
from lhc.io.bgzf import compress


class TestIndexedFastaSet(unittest.TestCase):
    def setUp(self):
        fhndl, self.fname = tempfile.mkstemp()
        os.write(fhndl, '>a x\naaaaaaaaaa\nbbbbbbbbbb\ncccccccccc\ndddddddddd\neeeeeeeeee\n>b y\nffffffffff\ngggggggggg\nhhhhh')
        os.close(fhndl)

        index(self.fname)

        fhndl, self.fname_compressed = tempfile.mkstemp()
        os.write(fhndl, '>a\n')
        for base in 'acgtu':
            for i in xrange(200):
                os.write(fhndl, 100 * base)
                os.write(fhndl, '\n')
        os.write(fhndl, '>b\n')
        for base in 'utgca':
            for i in xrange(200):
                os.write(fhndl, 100 * base)
                os.write(fhndl, '\n')
        os.close(fhndl)
        compress(self.fname_compressed)
        index('{}.bgz'.format(self.fname_compressed))
    
    def test_get_by_key(self):
        parser = IndexedFastaSet(self.fname)
        
        self.assertEquals('aaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeee', str(parser['a']))
        self.assertEquals('ffffffffffgggggggggghhhhh', str(parser['b']))
    
    def test_get_by_position(self):
        parser = IndexedFastaSet(self.fname)
        
        self.assertEquals('b', parser.fetch('a', 10, 11))
        self.assertEquals('g', parser.fetch('b', 10, 11))
    
    def test_get_by_interval(self):
        parser = IndexedFastaSet(self.fname)
        
        self.assertEquals('bbbbbbbbbb', parser.fetch('a', 10, 20))
        self.assertEquals('gggggggggg', parser.fetch('b', 10, 20))
        self.assertEquals('aaaaabbbbb', parser.fetch('a', 5, 15))
        self.assertEquals('fffffggggg', parser.fetch('b', 5, 15))

    def test_get_by_key_compressed(self):
        parser = IndexedFastaSet('{}.bgz'.format(self.fname_compressed))

        self.assertEquals(100 * 'u', parser['a'][80000:80100])
        self.assertEquals(100 * 'a', parser['b'][80000:80100])

    def test_get_by_position_compressed(self):
        parser = IndexedFastaSet('{}.bgz'.format(self.fname_compressed))

        self.assertEquals('u', parser.fetch('a', 80000, 80001))
        self.assertEquals('a', parser.fetch('b', 80000, 80001))

    def test_get_by_interval_compressed(self):
        parser = IndexedFastaSet('{}.bgz'.format(self.fname_compressed))

        self.assertEquals(100 * 'u', parser.fetch('a', 80000, 80100))
        self.assertEquals(100 * 'a', parser.fetch('b', 80000, 80100))

    def tearDown(self):
        os.remove(self.fname)
        os.remove('{}.fai'.format(self.fname))

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
