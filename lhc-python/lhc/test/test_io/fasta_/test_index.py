import os
import tempfile
import unittest

from subprocess import Popen

from lhc.binf.genomic_coordinate import Position, Interval
try:
    from lhc.io.fasta_.index import IndexedFastaFile
    import_failed = False
except ImportError:
    import_failed = True


class TestFasta(unittest.TestCase):
    
    def setUp(self):
        if import_failed:
            self.skipTest('Could not import IndexedFastaFile.')

        fhndl, self.fname = tempfile.mkstemp()
        os.write(fhndl, '>a x\naaaaaaaaaa\nbbbbbbbbbb\ncccccccccc\ndddddddddd\neeeeeeeeee\n>b y\nffffffffff\ngggggggggg\nhhhhh')
        os.close(fhndl)

        prc = Popen(['samtools', 'faidx', '%s'%self.fname])
        prc.wait()
    
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

