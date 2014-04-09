import os
import tempfile
import unittest

from lhc.binf.genomic_coordinate import Interval
from lhc.file_format import gtf

class TestGtf(unittest.TestCase):
    
    def setUp(self):
        fhndl, self.fname = tempfile.mkstemp()
        os.write(fhndl, 'chr1\t.\tgene\t1000\t2000\t0\t+\t0\tgene_name "a"\n' +\
            'chr1\t.\ttranscript\t1000\t2000\t0\t+\t0\tgene_name "a";transcript_name "a.0"\n' +\
            'chr1\t.\tCDS\t1100\t1300\t0\t+\t0\tgene_name "a";transcript_name "a.0"\n' +\
            'chr1\t.\tCDS\t1330\t1600\t0\t+\t0\tgene_name "a";transcript_name "a.0"\n' +\
            'chr1\t.\tCDS\t1660\t1900\t0\t+\t0\tgene_name "a";transcript_name "a.0"\n' +\
            'chr1\t.\ttranscript\t1000\t2000\t0\t+\t0\tgene_name "a";transcript_name "a.1"\n' +\
            'chr1\t.\tCDS\t1100\t1300\t0\t+\t0\tgene_name "a";transcript_name "a.1"\n' +\
            'chr1\t.\tCDS\t1660\t1900\t0\t+\t0\tgene_name "a";transcript_name "a.1"\n' +\
            'chr1\t.\tgene\t5000\t6000\t0\t+\t0\tgene_name "b"\n' +\
            'chr1\t.\ttranscript\t5000\t6000\t0\t+\t0\tgene_name "b";transcript_name "b.0"\n' +\
            'chr1\t.\tCDS\t5100\t5900\t0\t+\t0\tgene_name "b";transcript_name "b.0"\n')
        os.close(fhndl)
    
    def test_iterEntries(self):
        it = gtf.iterEntries(self.fname)
        
        gene = it.next()
        self.assertEquals(gene.name, 'a')
        self.assertEquals(len(gene.transcripts), 2)
        self.assertEquals(gene.transcripts.values()[0].name, 'a.0')
        self.assertEquals(gene.transcripts.values()[1].name, 'a.1')
        self.assertEquals(len(gene.transcripts.values()[0].exons), 3)
        self.assertEquals(len(gene.transcripts.values()[1].exons), 2)
        
        gene = it.next()
        self.assertEquals(gene.name, 'b')
        self.assertEquals(len(gene.transcripts), 1)
        self.assertEquals(gene.transcripts.values()[0].name, 'b.0')
        self.assertEquals(len(gene.transcripts.values()[0].exons), 1)
        
        self.assertRaises(StopIteration, it.next)
    
    def test_getItemByKey(self):
        parser = gtf.GtfParser(self.fname)
        
        gene = parser['a']
        self.assertEquals(gene.name, 'a')
        self.assertEquals(len(gene.transcripts), 2)
        self.assertEquals(gene.transcripts.values()[0].name, 'a.0')
        self.assertEquals(gene.transcripts.values()[1].name, 'a.1')
        self.assertEquals(len(gene.transcripts.values()[0].exons), 3)
        self.assertEquals(len(gene.transcripts.values()[1].exons), 2)
        
        gene = parser['b']
        self.assertEquals(gene.name, 'b')
        self.assertEquals(len(gene.transcripts), 1)
        self.assertEquals(gene.transcripts.values()[0].name, 'b.0')
        self.assertEquals(len(gene.transcripts.values()[0].exons), 1)
     
    def test_getItemInterval(self):
        parser = gtf.GtfParser(self.fname)
        
        genes = parser[Interval('chr1', 500, 1500)]
        self.assertEquals(len(genes), 1)
        self.assertEquals(genes[0].name, 'a')
        
        genes = parser[Interval('chr1', 1500, 5500)]
        self.assertEquals(len(genes), 2)
        self.assertEquals(set(gene.name for gene in genes), set('ab'))
 
    def test_getItemIndexedByKey(self):
        gtf.index(self.fname)
        parser = gtf.GtfParser(self.fname)
        
        gene = parser['a']
        self.assertEquals(gene.name, 'a')
        self.assertEquals(len(gene.transcripts), 2)
        self.assertEquals(gene.transcripts.values()[0].name, 'a.0')
        self.assertEquals(gene.transcripts.values()[1].name, 'a.1')
        self.assertEquals(len(gene.transcripts.values()[0].exons), 3)
        self.assertEquals(len(gene.transcripts.values()[1].exons), 2)
        
        gene = parser['b']
        self.assertEquals(gene.name, 'b')
        self.assertEquals(len(gene.transcripts), 1)
        self.assertEquals(gene.transcripts.values()[0].name, 'b.0')
        self.assertEquals(len(gene.transcripts.values()[0].exons), 1)
    
    def test_getItemIndexedInterval(self):
        gtf.index(self.fname)
        parser = gtf.GtfParser(self.fname)
        
        genes = parser[Interval('chr1', 500, 1500)]
        self.assertEquals(len(genes), 1)
        self.assertEquals(genes[0].name, 'a')
        
        genes = parser[Interval('chr1', 1500, 5500)]
        self.assertEquals(len(genes), 2)
        self.assertEquals(set(gene.name for gene in genes), set('ab'))
    
    def tearDown(self):
        os.remove(self.fname)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())

