import unittest
import tempfile

from collections import OrderedDict
from lhc.binf.genomic_coordinate import Interval
from lhc.binf.gene_model import Gene, Transcript, Exon
from lhc.binf.collection.model_set2 import ModelSet

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
    
    def test_init(self):
        cur = self.model_set.conn.cursor()
        
        qry = 'SELECT * FROM model'
        self.assertEquals(list(cur.execute(qry)), [(1, 1, u'1', u'+', u'gene', u'00', 0, None, 0, 15),
            (2, 1, u'1', u'+', u'transcript', u'00.0', 0, 1, 1, 8),
            (3, 4, u'1', u'+', u'CDS', None, 0, 2, 2, 3),
            (4, 5, u'1', u'+', u'CDS', None, 1, 2, 4, 5),
            (5, 6, u'1', u'+', u'CDS', None, 2, 2, 6, 7),
            (6, 1, u'1', u'+', u'transcript', u'00.1', 1, 1, 9, 14),
            (7, 4, u'1', u'+', u'CDS', None, 0, 6, 10, 11),
            (8, 6, u'1', u'+', u'CDS', None, 1, 6, 12, 13),
            (9, 2, u'1', u'+', u'gene', u'01', 1, None, 16, 31),
            (10, 2, u'1', u'+', u'transcript', u'01.0', 0, 9, 17, 24),
            (11, 7, u'1', u'+', u'CDS', None, 0, 10, 18, 19),
            (12, 8, u'1', u'+', u'CDS', None, 1, 10, 20, 21),
            (13, 9, u'1', u'+', u'CDS', None, 2, 10, 22, 23),
            (14, 2, u'1', u'+', u'transcript', u'01.1', 1, 9, 25, 30),
            (15, 7, u'1', u'+', u'CDS', None, 0, 14, 26, 27),
            (16, 9, u'1', u'+', u'CDS', None, 1, 14, 28, 29),
            (17, 3, u'1', u'+', u'gene', u'02', 2, None, 32, 47),
            (18, 3, u'1', u'+', u'transcript', u'02.0', 0, 17, 33, 40),
            (19, 10, u'1', u'+', u'CDS', None, 0, 18, 34, 35),
            (20, 11, u'1', u'+', u'CDS', None, 1, 18, 36, 37),
            (21, 12, u'1', u'+', u'CDS', None, 2, 18, 38, 39),
            (22, 3, u'1', u'+', u'transcript', u'02.1', 1, 17, 41, 46),
            (23, 10, u'1', u'+', u'CDS', None, 0, 22, 42, 43),
            (24, 12, u'1', u'+', u'CDS', None, 1, 22, 44, 45),
            (25, 3, u'2', u'+', u'gene', u'03', 3, None, 48, 63),
            (26, 3, u'2', u'+', u'transcript', u'03.0', 0, 25, 49, 56),
            (27, 10, u'2', u'+', u'CDS', None, 0, 26, 50, 51),
            (28, 11, u'2', u'+', u'CDS', None, 1, 26, 52, 53),
            (29, 12, u'2', u'+', u'CDS', None, 2, 26, 54, 55),
            (30, 3, u'2', u'+', u'transcript', u'03.1', 1, 25, 57, 62),
            (31, 10, u'2', u'+', u'CDS', None, 0, 30, 58, 59),
            (32, 12, u'2', u'+', u'CDS', None, 1, 30, 60, 61)
        ])
        
        qry = 'SELECT * FROM interval'
        self.assertEquals(list(cur.execute(qry)), [(1, 1000, 2000, 2),
            (2, 3000, 4000, 3),
            (3, 5000, 6000, 4),
            (4, 1000, 1200, 0),
            (5, 1400, 1600, 0),
            (6, 1800, 2000, 0),
            (7, 3000, 3200, 0),
            (8, 3400, 3600, 0),
            (9, 3800, 4000, 0),
            (10, 5000, 5200, 0),
            (11, 5400, 5600, 0),
            (12, 5800, 6000, 0)
        ])
        
        qry = 'SELECT * FROM sublist'
        self.assertEquals(list(cur.execute(qry)), [(1, 1, 3),
            (2, 4, 3),
            (3, 7, 3),
            (4, 10, 3)
        ])

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
