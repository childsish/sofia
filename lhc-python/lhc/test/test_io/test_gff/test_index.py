import os
import pkgutil
import pysam
import tempfile
import unittest

from lhc.io.gff_.index import IndexedGffFile


class TestIndexedVcfFile(unittest.TestCase):
    def setUp(self):
        self.dirname = tempfile.mkdtemp()
        self.filename = 'tmp.gff.gz'

        fileobj = open(os.path.join(self.dirname, self.filename), 'wb')
        fileobj.write(pkgutil.get_data('lhc.test', 'data/randome.gff.gz'))
        fileobj.close()

        fileobj = open(os.path.join(self.dirname, self.filename + '.tbi'), 'wb')
        fileobj.write(pkgutil.get_data('lhc.test', 'data/randome.gff.gz.tbi'))
        fileobj.close()

        self.index = pysam.TabixFile(os.path.join(self.dirname, self.filename))

    def test_fetch(self):
        parser = IndexedGffFile(self.index)

        genomic_features = parser.fetch('chr1', 99)
        self.assertEqual(1, len(genomic_features))
        self.assertEquals('chr1', genomic_features[0].chr)
        self.assertEquals(50, genomic_features[0].start)
        self.assertEquals(211, genomic_features[0].stop)
        self.assertEquals({'ID': 'gene0'}, genomic_features[0].data)
        self.assertEquals('gene0', genomic_features[0].name)
        self.assertEquals('+', genomic_features[0].strand)
        self.assertEquals('gene', genomic_features[0].type)

        genomic_features = parser.fetch('chr2', 100, 1000)
        self.assertEqual(2, len(genomic_features))

    def tearDown(self):
        self.index.close()
        os.remove(os.path.join(self.dirname, self.filename))
        os.remove(os.path.join(self.dirname, self.filename + '.tbi'))
        os.rmdir(self.dirname)


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
