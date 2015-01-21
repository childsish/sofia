import os
import tempfile
import unittest

from lhc.io.fasta_.iterator import FastaEntryIterator


class TestFasta(unittest.TestCase):
    
    def setUp(self):
        fhndl, self.fname = tempfile.mkstemp()
        os.write(fhndl, '>a x\naaaaaaaaaa\nbbbbbbbbbb\ncccccccccc\ndddddddddd\neeeeeeeeee\n>b y\nffffffffff\ngggggggggg\nhhhhh')
        os.close(fhndl)

    def test_iterEntries(self):
        it = FastaEntryIterator(self.fname)
        
        self.assertEquals(tuple(it.next()), ('a', 'aaaaaaaaaabbbbbbbbbbccccccccccddddddddddeeeeeeeeee'))
        self.assertEquals(tuple(it.next()), ('b', 'ffffffffffgggggggggghhhhh'))
        self.assertRaises(StopIteration, it.next)

    def tearDown(self):
        os.remove(self.fname)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
