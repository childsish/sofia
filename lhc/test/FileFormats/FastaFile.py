import os
import tempfile

from lhc.FileFormats.FastaFile import *
from unittest import TestCase, main

class TestFastaFile(TestCase):
    def setUp(self):
        self.hdr1 = '1'
        self.hdr2 = '2'
        self.seq1 = ['aaaaaaaaaa', 'cccccccccc', 'tttttttttt', 'gggggggggg']
        self.seq2 = ['acacacacac', 'tgtgtgtgtg', 'ccaaccaacc', 'ggttggttgg']
        fhndl, self.fname = tempfile.mkstemp()
        os.write(fhndl, '>%s comment\n%s\n>%s comment\n%s'%\
            (self.hdr1, '\n'.join(self.seq1), self.hdr2, '\n'.join(self.seq2)))
        os.close(fhndl)

        iname = getIndexName(self.fname)
        if os.path.exists(iname):
            os.remove(iname)
        indexFasta(self.fname)
        
    def test_iterNormal(self):
        it = iterNormalFasta(self.fname)

        self.assertEquals(it.next(),
            ('%s comment'%self.hdr1, ''.join(self.seq1)))
        self.assertEquals(it.next(),
            ('%s comment'%self.hdr2, ''.join(self.seq2)))
    
    def test_extractNormal(self):
        extract = extractNormalFasta
        self.assertEquals(extract(self.fname, '1'), ''.join(self.seq1))
        self.assertEquals(extract(self.fname, '2'), ''.join(self.seq2))
    
    def test_offsetCalculation(self):
        it = iterIndexedFasta(getIndexName(self.fname))
        hdr, seq = it.next()
        
        self.assertEquals(seq.convertPositionToIndex(9), 20)
        self.assertEquals(seq.convertPositionToIndex(10), 22)
        self.assertEquals(seq.convertPositionToIndex(19), 31)
        self.assertEquals(seq.convertPositionToIndex(20), 33)
    
    def test_iterIndexed(self):
        it = iterIndexedFasta(getIndexName(self.fname))
        
        hdr, seq = it.next()
        self.assertEquals((hdr, str(seq)),
            ('%s comment'%self.hdr1, ''.join(self.seq1)))
        hdr, seq = it.next()
        self.assertEquals((hdr, str(seq)),
            ('%s comment'%self.hdr2, ''.join(self.seq2)))
    
    def test_extractIndexed(self):
        seq1 = extractIndexedFasta(self.fname, '1')
        seq2 = extractIndexedFasta(self.fname, '2')
        
        self.assertEquals(str(seq1), ''.join(self.seq1))
        self.assertEquals(str(seq2), ''.join(self.seq2))
    
    def test_extractSubIndexed(self):
        seq1 = extractIndexedFasta(self.fname, '1')
        seq2 = extractIndexedFasta(self.fname, '2')
        
        self.assertEquals(str(seq1[5:15]), ''.join(self.seq1)[5:15])
        self.assertEquals(str(seq1[20:25]), ''.join(self.seq1)[20:25])
        self.assertEquals(str(seq1[25:30]), ''.join(self.seq1)[25:30])
        self.assertEquals(str(seq2[5:15]), ''.join(self.seq2)[5:15])
        self.assertEquals(str(seq2[20:25]), ''.join(self.seq2)[20:25])
        self.assertEquals(str(seq2[25:30]), ''.join(self.seq2)[25:30])
        
if __name__ == '__main__':
    import sys
    sys.exit(main())
