import cPickle
import os
import tempfile
import unittest

from lhc.indices.fasta import FastaIndex
from lhc.binf.genomic_coordinate import GenomicPosition as Position

class TestFastaIndex(unittest.TestCase):
    
    def setUp(self):
        self.fhndl, self.fname = tempfile.mkstemp()
        os.write(self.fhndl, '>chr1\naaaaaccccc\ngggggttttt\n>chr2\ngggggaaaaa\ntttttccccc\n')
        os.close(self.fhndl)
    
    def test_setGet(self):
        index = FastaIndex(self.fname)
        index['chr1'] = 6
        index['chr2'] = 34

        infile = open(self.fname)
        infile.seek(index[Position('chr1', 0)])
        self.assertEquals(infile.read(1), 'a')
        infile.seek(index[Position('chr1', 4)])
        self.assertEquals(infile.read(1), 'a')
        infile.seek(index[Position('chr1', 5)])
        self.assertEquals(infile.read(1), 'c')
        infile.seek(index[Position('chr1', 10)])
        self.assertEquals(infile.read(1), 'g')
        infile.seek(index[Position('chr1', 15)])
        self.assertEquals(infile.read(1), 't')
        infile.seek(index[Position('chr2', 0)])
        self.assertEquals(infile.read(1), 'g')
        infile.seek(index[Position('chr2', 19)])
        self.assertEquals(infile.read(1), 'c')
        infile.close()
    
    def test_pickle(self):
        index = FastaIndex(self.fname)
        index['chr1'] = 6
        index['chr2'] = 34
        outfile = open('%s.idx'%self.fname, 'w')
        cPickle.dump(index, outfile)
        outfile.close()

        infile = open('%s.idx'%self.fname)
        index = cPickle.load(infile)
        infile.close()
        os.remove('%s.idx'%self.fname)
        infile = open(self.fname)
        infile.seek(index[Position('chr1', 0)])
        self.assertEquals(infile.read(1), 'a')
        infile.seek(index[Position('chr2', 19)])
        self.assertEquals(infile.read(1), 'c')
        infile.close()

    
    def tearDown(self):
        os.remove(self.fname)

if __name__ == '__main__':
    unittest.main()

