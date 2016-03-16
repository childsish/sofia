import os
import pkgutil
import pysam
import tempfile
import unittest

from lhc.io.vcf_.index import IndexedVcfFile


class TestIndexedVcfFile(unittest.TestCase):
    def setUp(self):
        self.dirname = tempfile.mkdtemp()
        self.filename = 'tmp.vcf.gz'

        fileobj = open(os.path.join(self.dirname, self.filename), 'wb')
        fileobj.write(pkgutil.get_data('lhc.test', 'data/randome.vcf.gz'))
        fileobj.close()

        fileobj = open(os.path.join(self.dirname, self.filename + '.tbi'), 'wb')
        fileobj.write(pkgutil.get_data('lhc.test', 'data/randome.vcf.gz.tbi'))
        fileobj.close()

        self.index = pysam.TabixFile(os.path.join(self.dirname, self.filename))

    def test_fetch(self):
        parser = IndexedVcfFile(os.path.join(self.dirname, self.filename), self.index)

        variants = parser.fetch('chr1', 99)
        self.assertEqual(1, len(variants))
        self.assertEquals('chr1', variants[0].chr)
        self.assertEquals(99, variants[0].pos)
        self.assertEquals('.', variants[0].id)
        self.assertEquals('A', variants[0].ref)
        self.assertEquals('C', variants[0].alt)
        self.assertAlmostEquals(100, variants[0].qual)
        self.assertEquals('PASS', variants[0].filter)
        self.assertEquals({'RO': '50', 'AO': '50', 'AF': '0.5'}, variants[0].info)
        self.assertEquals({}, variants[0].samples)

        variants = parser.fetch('chr2', 100, 1000)
        self.assertEqual(15, len(variants))

    def tearDown(self):
        self.index.close()
        os.remove(os.path.join(self.dirname, self.filename))
        os.remove(os.path.join(self.dirname, self.filename + '.tbi'))
        os.rmdir(self.dirname)


if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
