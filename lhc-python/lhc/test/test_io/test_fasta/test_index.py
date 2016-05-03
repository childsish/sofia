import os
import pkgutil
import tempfile
import unittest

try:
    import pysam
    from lhc.io.fasta_.index import IndexedFastaSet
except ImportError:
    pysam = None
    IndexedFastaSet = None


@unittest.skipIf(pysam is None, 'could not import pysam')
class TestIndexedFastaSet(unittest.TestCase):
    def setUp(self):
        self.dirname = tempfile.mkdtemp()
        self.filename = 'tmp.fasta.gz'

        fileobj = open(os.path.join(self.dirname, self.filename), 'wb')
        fileobj.write(pkgutil.get_data('lhc.test', 'data/randome.fasta.gz'))
        fileobj.close()

        fileobj = open(os.path.join(self.dirname, self.filename + '.fai'), 'wb')
        fileobj.write(pkgutil.get_data('lhc.test', 'data/randome.fasta.gz.fai'))
        fileobj.close()

        fileobj = open(os.path.join(self.dirname, self.filename + '.gzi'), 'wb')
        fileobj.write(pkgutil.get_data('lhc.test', 'data/randome.fasta.gz.gzi'))
        fileobj.close()

        self.index = pysam.FastaFile(os.path.join(self.dirname, self.filename))

    def test_get_item(self):
        parser = IndexedFastaSet(self.index)

        self.assertEquals('CGACAACACACTCCGGGTAAAACAATGATCGACAGGGAACCACCACATACCTCCTTCACCGAGTTGTTAGTGTACGCCTTTTTGTTGTGATGATTAAATG', parser['chr1'][100:200])
        self.assertEquals('CGACCTACAGGCTTCGTGTGCGAGCTAAACTTGAGGCCGCCGTCCAGCGATCATCGTGTGTCTAGCAGGAAGCTTCTGGTAACGAAGATCGTTAAGCAGG', parser['chr2'][100:200])

    def test_get_fetch(self):
        parser = IndexedFastaSet(self.index)

        self.assertEquals('C', parser.fetch('chr1', 100))
        self.assertEquals('C', parser.fetch('chr2', 100))

        self.assertEquals('CGACAACACACTCCGGGTAAAACAATGATCGACAGGGAACCACCACATACCTCCTTCACCGAGTTGTTAGTGTACGCCTTTTTGTTGTGATGATTAAATG', parser.fetch('chr1', 100, 200))
        self.assertEquals('CGACCTACAGGCTTCGTGTGCGAGCTAAACTTGAGGCCGCCGTCCAGCGATCATCGTGTGTCTAGCAGGAAGCTTCTGGTAACGAAGATCGTTAAGCAGG', parser.fetch('chr2', 100, 200))

    def tearDown(self):
        self.index.close()
        os.remove(os.path.join(self.dirname, self.filename))
        os.remove(os.path.join(self.dirname, self.filename + '.fai'))
        os.remove(os.path.join(self.dirname, self.filename + '.gzi'))
        os.rmdir(self.dirname)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
