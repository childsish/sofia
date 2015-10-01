import os
import tempfile
import unittest

try:
    from lhc.io.fasta_.index import IndexedFastaSet
except ImportError:
    pass

@unittest.skip
class TestIndexedFastaSet(unittest.TestCase):
    def setUp(self):
        fhndl, self.fname = tempfile.mkstemp()
        os.write(fhndl, '>a\n')
        for base in 'acgtu':
            for i in xrange(10):
                os.write(fhndl, 100 * base)
                os.write(fhndl, '\n')
        os.write(fhndl, '>b\n')
        for base in 'utgca':
            for i in xrange(10):
                os.write(fhndl, 100 * base)
                os.write(fhndl, '\n')
        os.close(fhndl)

        #compress(self.fname)

    def test_get_by_key(self):
        parser = IndexedFastaSet('{}.bgz'.format(self.fname))

        self.assertEquals(200 * 'u', parser['a'][4000:4200])
        self.assertEquals(200 * 'a', parser['b'][4000:4200])

    def test_get_by_position(self):
        parser = IndexedFastaSet('{}.bgz'.format(self.fname))

        self.assertEquals('u', parser.fetch('a', 4000, 4001))
        self.assertEquals('a', parser.fetch('b', 4000, 4001))

    def test_get_by_interval(self):
        parser = IndexedFastaSet('{}.bgz'.format(self.fname))

        self.assertEquals(200 * 'u', parser.fetch('a', 4000, 4200))
        self.assertEquals('c' + 199 * 'a', parser.fetch('b', 3999, 4199))
        self.assertEquals('c' + 200 * 'a', parser.fetch('b', 3999, 4200))
        self.assertEquals(199 * 'a', parser.fetch('b', 4000, 4199))
        self.assertEquals(200 * 'a', parser.fetch('b', 4000, 4200))

    def tearDown(self):
        os.remove(self.fname)
        os.remove('{}.bgz'.format(self.fname))
        os.remove('{}.bgz.lci'.format(self.fname))

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
