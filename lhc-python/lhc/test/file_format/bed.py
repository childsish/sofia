import os
import tempfile
import unittest

from subprocess import Popen, PIPE

from lhc.binf.genomic_coordinate import Interval
from lhc.file_format.bed_.index import IndexedBedFile

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

        prc = Popen(['bgzip', self.fname])
        prc.wait()
        prc = Popen(['tabix', '-p', 'bed', '%s.gz'%self.fname])
        prc.wait()

    def test_indexedBed(self):
        bed = IndexedBedFile('%s.gz'%self.fname)

        res = bed[Interval('chr1', 100, 200)]
        self.assertEquals(len(res), 2)
        self.assertEquals(res[0].chr, 'chr1')
        self.assertEquals(res[0].start, 99)
        self.assertEquals(res[0].stop, 200)
        self.assertEquals(res[1].chr, 'chr1')
        self.assertEquals(res[1].start, 149)
        self.assertEquals(res[1].stop, 250)
    
    def tearDown(self):
        os.remove('%s.gz'%self.fname)
        os.remove('%s.gz.tbi'%self.fname)
        
if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())

