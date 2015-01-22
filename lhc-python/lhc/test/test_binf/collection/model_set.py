import unittest
import tempfile

from collections import OrderedDict
from lhc.binf.genomic_coordinate import Interval
from lhc.binf.gene_model import Gene, Transcript, Exon
from lhc.binf.collection.model_set import ModelSet

class TestModelSet(unittest.TestCase):
    
    def setUp(self):
        self.hndl, self.fname = tempfile.mkstemp()
        self.genes = [
            Gene('00', Interval('1', 1000, 2000), OrderedDict([
                ('00.0', Transcript('00.0', Interval('1', 1000, 2000), [
                    Exon(Interval('1', 1000, 1200), 'CDS'),
                    Exon(Interval('1', 1400, 1600), 'CDS'),
                    Exon(Interval('1', 1800, 2000), 'CDS')
                ])),
                ('00.1', Transcript('00.1', Interval('1', 1000, 2000), [
                    Exon(Interval('1', 1000, 1200), 'CDS'),
                    Exon(Interval('1', 1800, 2000), 'CDS')
                ]))
            ])),
            Gene('01', Interval('1', 3000, 4000), OrderedDict([
                ('01.0', Transcript('01.0', Interval('1', 3000, 4000), [
                    Exon(Interval('1', 3000, 3200), 'CDS'),
                    Exon(Interval('1', 3400, 3600), 'CDS'),
                    Exon(Interval('1', 3800, 4000), 'CDS')
                ])),
                ('01.1', Transcript('01.1', Interval('1', 3000, 4000), [
                    Exon(Interval('1', 3000, 3200), 'CDS'),
                    Exon(Interval('1', 3800, 4000), 'CDS')
                ]))
            ])),
            Gene('02', Interval('1', 5000, 6000), OrderedDict([
                ('02.0', Transcript('02.0', Interval('1', 5000, 6000), [
                    Exon(Interval('1', 5000, 5200), 'CDS'),
                    Exon(Interval('1', 5400, 5600), 'CDS'),
                    Exon(Interval('1', 5800, 6000), 'CDS')
                ])),
                ('02.1', Transcript('02.1', Interval('1', 5000, 6000), [
                    Exon(Interval('1', 5000, 5200), 'CDS'),
                    Exon(Interval('1', 5800, 6000), 'CDS')
                ]))
            ])),
            Gene('03', Interval('2', 5000, 6000), OrderedDict([
                ('03.0', Transcript('03.0', Interval('2', 5000, 6000), [
                    Exon(Interval('2', 5000, 5200), 'CDS'),
                    Exon(Interval('2', 5400, 5600), 'CDS'),
                    Exon(Interval('2', 5800, 6000), 'CDS')
                ])),
                ('03.1', Transcript('03.1', Interval('2', 5000, 6000), [
                    Exon(Interval('2', 5000, 5200), 'CDS'),
                    Exon(Interval('2', 5800, 6000), 'CDS')
                ]))
            ]))]
        
        self.model_set = ModelSet(self.fname, self.genes)
    
    def test_get(self):
        gene = self.model_set.get('00')
        self.assertEquals(gene.name, '00')
        self.assertEquals(gene.ivl, Interval('1', 1000, 2000))
        self.assertEquals(gene.transcripts.keys(), ['00.0', '00.1'])
        self.assertEquals(gene.transcripts['00.0'].ivl, Interval('1', 1000, 2000))
        self.assertEquals(gene.transcripts['00.1'].ivl, Interval('1', 1000, 2000))
        self.assertEquals(len(gene.transcripts['00.0'].exons), 3)
        self.assertEquals([exon.ivl for exon in gene.transcripts['00.0'].exons],
            [Interval('1', 1000, 1200), Interval('1', 1400, 1600), Interval('1', 1800, 2000)])
        self.assertEquals(len(gene.transcripts['00.1'].exons), 2)
        self.assertEquals([exon.ivl for exon in gene.transcripts['00.1'].exons],
            [Interval('1', 1000, 1200), Interval('1', 1800, 2000)])
        
        gene = self.model_set.get('01')
        self.assertEquals(gene.name, '01')
        self.assertEquals(gene.ivl, Interval('1', 3000, 4000))
        self.assertEquals(gene.transcripts.keys(), ['01.0', '01.1'])
        self.assertEquals(gene.transcripts['01.0'].ivl, Interval('1', 3000, 4000))
        self.assertEquals(gene.transcripts['01.1'].ivl, Interval('1', 3000, 4000))
        self.assertEquals(len(gene.transcripts['01.0'].exons), 3)
        self.assertEquals([exon.ivl for exon in gene.transcripts['01.0'].exons],
            [Interval('1', 3000, 3200), Interval('1', 3400, 3600), Interval('1', 3800, 4000)])
        self.assertEquals(len(gene.transcripts['01.1'].exons), 2)
        self.assertEquals([exon.ivl for exon in gene.transcripts['01.1'].exons],
            [Interval('1', 3000, 3200), Interval('1', 3800, 4000)])
     
    def test_intersect(self):
        res = self.model_set.intersect(Interval('1', 1000, 6000))
        self.assertEquals(len(res), 3)
        
        res = self.model_set.intersect(Interval('2', 1000, 6000))
        self.assertEquals(len(res), 1)

if __name__ == "__main__":
    unittest.main()
