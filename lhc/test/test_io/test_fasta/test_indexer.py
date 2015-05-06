import unittest

from StringIO import StringIO
from lhc.io.fasta_.indexer import FastaIndexer


class TestFastaIndexer(unittest.TestCase):
    def test_indexer(self):
        in_string = StringIO('>chr1\naaccggtt\naaccggtt\naa\n>chr2\naaacccgggtttt\naaacccgggtttt\na')
        indexer = FastaIndexer(in_string)

        self.assertEquals(('chr1', 18, 6, 8, 9), indexer.next())
        self.assertEquals(('chr2', 35, 33, 8, 9), indexer.next())
        self.assertRaises(StopIteration, indexer.next)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
