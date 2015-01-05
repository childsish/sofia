import os
import tempfile
import unittest

from subprocess import Popen
from lhc.binf.genomic_coordinate import Interval
from lhc.file_format.gtf_.iterator import GtfEntityIterator
from lhc.file_format.gtf_.set_ import GtfSet
from lhc.file_format.gtf_.index import IndexedGtfFile

class TestGtf(unittest.TestCase):
    
    def setUp(self):
        fhndl, self.fname = tempfile.mkstemp()
        os.write(fhndl, 'chr1\t.\tgene\t1000\t2000\t0\t+\t0\tgene_name "a"\n'\
            'chr1\t.\ttranscript\t1000\t2000\t0\t+\t0\tgene_name "a";transcript_name "a.0"\n'\
            'chr1\t.\tCDS\t1100\t1300\t0\t+\t0\tgene_name "a";transcript_name "a.0"\n'\
            'chr1\t.\tCDS\t1330\t1600\t0\t+\t0\tgene_name "a";transcript_name "a.0"\n'\
            'chr1\t.\tCDS\t1660\t1900\t0\t+\t0\tgene_name "a";transcript_name "a.0"\n'\
            'chr1\t.\ttranscript\t1000\t2000\t0\t+\t0\tgene_name "a";transcript_name "a.1"\n'\
            'chr1\t.\tCDS\t1100\t1300\t0\t+\t0\tgene_name "a";transcript_name "a.1"\n'\
            'chr1\t.\tCDS\t1660\t1900\t0\t+\t0\tgene_name "a";transcript_name "a.1"\n'\
            'chr1\t.\tgene\t5000\t6000\t0\t+\t0\tgene_name "b"\n'\
            'chr1\t.\ttranscript\t5000\t6000\t0\t+\t0\tgene_name "b";transcript_name "b.0"\n'\
            'chr1\t.\tCDS\t5100\t5900\t0\t+\t0\tgene_name "b";transcript_name "b.0"\n')
        os.close(fhndl)

        prc_stdout = open('%s.sorted'%self.fname, 'w')
        prc = Popen(['sort', '-k1,1', '-k4,4n', '-k5,5n', self.fname], stdout=prc_stdout)
        prc.wait()
        prc_stdout.close()
        prc = Popen(['mv', '%s.sorted'%self.fname, self.fname])
        prc.wait()
        prc = Popen(['bgzip', self.fname])
        prc.wait()
        prc = Popen(['tabix', '-p', 'gff', '%s.gz'%self.fname])
        prc.wait()
        prc = Popen(['python', '-m', 'lhc.file_format.gtf', 'index', '%s.gz'%self.fname])
        prc.wait()
    
    def test_iterEntries(self):
        it = GtfEntityIterator('%s.gz'%self.fname)
        
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
        parser = GtfSet(GtfEntityIterator('%s.gz'%self.fname))
        
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
        parser = GtfSet(GtfEntityIterator('%s.gz'%self.fname))
        
        genes = parser[Interval('chr1', 500, 1500)]
        self.assertEquals(len(genes), 1)
        self.assertEquals(genes[0].name, 'a')
        
        genes = parser[Interval('chr1', 1500, 5500)]
        self.assertEquals(len(genes), 2)
        self.assertEquals(set(gene.name for gene in genes), set('ab'))
 
    def test_getItemIndexedByKey(self):
        parser = IndexedGtfFile('%s.gz'%self.fname)
        
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
        parser = IndexedGtfFile('%s.gz'%self.fname)
        
        genes = parser[Interval('chr1', 500, 1500)]
        self.assertEquals(len(genes), 1)
        self.assertEquals(genes[0].name, 'a')
        
        genes = parser[Interval('chr1', 1500, 5500)]
        self.assertEquals(len(genes), 2)
        self.assertEquals(set(gene.name for gene in genes), set('ab'))
    
    def tearDown(self):
        os.remove('%s.gz'%self.fname)
        os.remove('%s.gz.tbi'%self.fname)
        os.remove('%s.gz.lhci'%self.fname)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())

