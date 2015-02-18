import os
import tempfile
import unittest

from lhc.io.txt_.compress import compress
from lhc.io.bed_.index import IndexedBedFile


class TestBed(unittest.TestCase):
    def setUp(self):
        fhndl, self.fname = tempfile.mkstemp()
        os.write(fhndl, 'chr1\t100\t200\t_00\t0.0\t+\n')
        os.write(fhndl, 'chr1\t150\t250\t_01\t0.0\t+\n')
        os.write(fhndl, 'chr1\t200\t300\t_02\t0.0\t+\n')
        os.write(fhndl, 'chr2\t100\t200\t_03\t0.0\t+\n')
        os.write(fhndl, 'chr2\t150\t250\t_04\t0.0\t+\n')
        os.write(fhndl, 'chr2\t200\t300\t_05\t0.0\t+\n')
        os.close(fhndl)

        compress(self.fname, ['1s', '2,3v'])

    def test_indexedBed(self):
        bed = IndexedBedFile('%s.bgz' % self.fname)

        res = bed.fetch('chr1', 100, 199)
        self.assertEquals(2, len(res))
        self.assertEquals(res[0].chr, 'chr1')
        self.assertEquals(res[0].start, 99)
        self.assertEquals(res[0].stop, 200)
        self.assertEquals(res[1].chr, 'chr1')
        self.assertEquals(res[1].start, 149)
        self.assertEquals(res[1].stop, 250)
    
    def tearDown(self):
        os.remove('%s.bgz' % self.fname)
        os.remove('%s.bgz.lci' % self.fname)
        
if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
