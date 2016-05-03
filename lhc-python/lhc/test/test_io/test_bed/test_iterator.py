import unittest

from lhc.io.bed_.iterator import BedEntryIterator


class TestBed(unittest.TestCase):
    def setUp(self):
        self.content = '''chr1\t100\t200\t_00\t0.0\t+
chr1\t150\t250\t_01\t0.0\t+
chr1\t200\t300\t_02\t0.0\t+
chr2\t100\t200\t_03\t0.0\t+
chr2\t150\t250\t_04\t0.0\t+
chr2\t200\t300\t_05\t0.0\t+
'''

    def test_iterator(self):
        it = BedEntryIterator(iter(self.content.split('\n')))

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
        
if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())

