import os
import shutil
import unittest
import tempfile

from lhc.binf.genomic_coordinate import Interval
from lhc.binf.gene_model import Gene, Transcript, Exon
from lhc.binf.collection.model_set2 import ModelSet

class TestModelSet(unittest.TestCase):
    
    def setUp(self):
        self.hndl, self.fname = tempfile.mkstemp()

    def test_get(self):
        model_set = ModelSet(self.fname, [
            Gene('00', Interval('1', 1000, 2000), {
                '00.0': Transcript('00.0', Interval('1', 1000, 2000), [
                    Exon(Interval('1', 1000, 1200), 'CDS'),
                    Exon(Interval('1', 1400, 1600), 'CDS'),
                    Exon(Interval('1', 1800, 2000), 'CDS')]),
                '00.1': Transcript('00.1', Interval('1', 1000, 2000), [
                    Exon(Interval('1', 1000, 1200), 'CDS'),
                    Exon(Interval('1', 1800, 2000), 'CDS')])}),
            Gene('01', Interval('1', 1000, 2000), {
                '01.0': Transcript('01.0', Interval('1', 1000, 2000), [
                    Exon(Interval('1', 1000, 1200), 'CDS'),
                    Exon(Interval('1', 1400, 1600), 'CDS'),
                    Exon(Interval('1', 1800, 2000), 'CDS')]),
                '01.1': Transcript('01.1', Interval('1', 1000, 2000), [
                    Exon(Interval('1', 1000, 1200), 'CDS'),
                    Exon(Interval('1', 1800, 2000), 'CDS')])})])
        
        gene0 = model_set.get('00')
        gene1 = model_set.get('01')
        
        self.assertEquals(set(['00.0', '00.1']), set(gene0.transcripts.keys()))
        self.assertEquals(set(['01.0', '01.1']), set(gene1.transcripts.keys()))
        self.assertEquals(len(gene0.transcripts['00.0'].exons), 3)
        self.assertEquals(len(gene0.transcripts['00.1'].exons), 2)
        self.assertEquals(len(gene1.transcripts['01.0'].exons), 3)
        self.assertEquals(len(gene1.transcripts['01.1'].exons), 2)

if __name__ == "__main__":
    unittest.main()
