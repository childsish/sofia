import os
import tempfile
import unittest

from lhc.io.fasta_.compress import compress
from lhc.io.fasta_.index import IndexedFastaSet


class TestCompressFasta(unittest.TestCase):
    def test_compress(self):
        fhndl, fname = tempfile.mkstemp()
        sequence_set = {}
        for chromosome in xrange(5):
            seq = []
            for i in xrange(100000):
                seq.append('_{:07d}'.format(i * 8))
            seq = ''.join(seq)
            sequence_set['chr{}'.format(chromosome + 1)] = seq
            os.write(fhndl, '>chr{}\n'.format(chromosome + 1))
            for i in xrange(0, len(seq), 100):
                os.write(fhndl, seq[i:i + 100])
                os.write(fhndl, '\n')
        os.close(fhndl)

        iname = compress(fname)
        index = IndexedFastaSet(iname)

        self.assertEqual(sequence_set['chr1'][100:200], index.fetch('chr1', 100, 200))
        self.assertEqual(sequence_set['chr1'][1100:1200], index.fetch('chr1', 1100, 1200))
        self.assertEqual(sequence_set['chr1'][5100:5200], index.fetch('chr1', 5100, 5200))
        self.assertEqual(sequence_set['chr1'][10100:10200], index.fetch('chr1', 10100, 10200))
        self.assertEqual(sequence_set['chr1'][50100:50200], index.fetch('chr1', 50100, 50200))

        self.assertEqual(sequence_set['chr2'][100:200], index.fetch('chr2', 100, 200))
        self.assertEqual(sequence_set['chr2'][1100:1200], index.fetch('chr2', 1100, 1200))
        self.assertEqual(sequence_set['chr2'][5100:5200], index.fetch('chr2', 5100, 5200))
        self.assertEqual(sequence_set['chr2'][10100:10200], index.fetch('chr2', 10100, 10200))
        self.assertEqual(sequence_set['chr2'][50100:50200], index.fetch('chr2', 50100, 50200))

        self.assertEqual(sequence_set['chr3'][100:200], index.fetch('chr3', 100, 200))
        self.assertEqual(sequence_set['chr3'][1100:1200], index.fetch('chr3', 1100, 1200))
        self.assertEqual(sequence_set['chr3'][5100:5200], index.fetch('chr3', 5100, 5200))
        self.assertEqual(sequence_set['chr3'][10100:10200], index.fetch('chr3', 10100, 10200))
        self.assertEqual(sequence_set['chr3'][50100:50200], index.fetch('chr3', 50100, 50200))

        self.assertEqual(sequence_set['chr4'][100:200], index.fetch('chr4', 100, 200))
        self.assertEqual(sequence_set['chr4'][1100:1200], index.fetch('chr4', 1100, 1200))
        self.assertEqual(sequence_set['chr4'][5100:5200], index.fetch('chr4', 5100, 5200))
        self.assertEqual(sequence_set['chr4'][10100:10200], index.fetch('chr4', 10100, 10200))
        self.assertEqual(sequence_set['chr4'][50100:50200], index.fetch('chr4', 50100, 50200))

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())