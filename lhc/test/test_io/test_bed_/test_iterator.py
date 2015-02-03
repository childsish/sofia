import os
import tempfile
import unittest

from lhc.io.bed_.iterator import BedEntryIterator


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

    def test_iterator(self):
        it = BedEntryIterator(self.fname)

        entry = it.next()
        self.assertEquals(('chr1', 99, 200, '_00'), (entry.ivl.chr, entry.ivl.start, entry.ivl.stop, entry.name))
        entry = it.next()
        self.assertEquals(('chr1', 149, 250, '_01'), (entry.ivl.chr, entry.ivl.start, entry.ivl.stop, entry.name))
        entry = it.next()
        self.assertEquals(('chr1', 199, 300, '_02'), (entry.ivl.chr, entry.ivl.start, entry.ivl.stop, entry.name))
        entry = it.next()
        self.assertEquals(('chr2', 99, 200, '_03'), (entry.ivl.chr, entry.ivl.start, entry.ivl.stop, entry.name))
        entry = it.next()
        self.assertEquals(('chr2', 149, 250, '_04'), (entry.ivl.chr, entry.ivl.start, entry.ivl.stop, entry.name))
        entry = it.next()
        self.assertEquals(('chr2', 199, 300, '_05'), (entry.ivl.chr, entry.ivl.start, entry.ivl.stop, entry.name))
    
    def tearDown(self):
        os.remove(self.fname)
        
if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())

