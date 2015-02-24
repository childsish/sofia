import os
import tempfile
import unittest

from lhc.io.gtf_.iterator import GtfEntryIterator
from lhc.io.gtf_.set_ import GtfSet


class TestGtf(unittest.TestCase):
    def setUp(self):
        fhndl, self.fname = tempfile.mkstemp()
        self.lines = [
            'chr1\t.\tgene\t1000\t2000\t0\t+\t0\tgene_id "a"',
            'chr1\t.\ttranscript\t1000\t2000\t0\t+\t0\tgene_id "a";transcript_id "a.0"',
            'chr1\t.\tCDS\t1100\t1300\t0\t+\t0\tgene_id "a";transcript_id "a.0"',
            'chr1\t.\tCDS\t1330\t1600\t0\t+\t0\tgene_id "a";transcript_id "a.0"',
            'chr1\t.\tCDS\t1660\t1900\t0\t+\t0\tgene_id "a";transcript_id "a.0"',
            'chr1\t.\ttranscript\t1000\t2000\t0\t+\t0\tgene_id "a";transcript_id "a.1"',
            'chr1\t.\tCDS\t1100\t1300\t0\t+\t0\tgene_id "a";transcript_id "a.1"',
            'chr1\t.\tCDS\t1660\t1900\t0\t+\t0\tgene_id "a";transcript_id "a.1"',
            'chr1\t.\tgene\t5000\t6000\t0\t+\t0\tgene_id "b"',
            'chr1\t.\ttranscript\t5000\t6000\t0\t+\t0\tgene_id "b";transcript_id "b.0"',
            'chr1\t.\tCDS\t5100\t5900\t0\t+\t0\tgene_id "b";transcript_id "b.0"'
        ]
        os.write(fhndl, '\n'.join(self.lines))
        os.close(fhndl)

    def test_getItemByKey(self):
        parser = GtfSet(GtfEntryIterator(self.fname))

        gene = parser['a']
        self.assertEquals(gene.name, 'a')
        self.assertEquals(len(gene.children), 2)
        self.assertEquals(gene.children[0].name, 'a.1')
        self.assertEquals(gene.children[1].name, 'a.0')
        self.assertEquals(len(gene.children[0].children), 2)
        self.assertEquals(len(gene.children[1].children), 3)

        gene = parser['b']
        self.assertEquals(gene.name, 'b')
        self.assertEquals(len(gene.children), 1)
        self.assertEquals(gene.children[0].name, 'b.0')
        self.assertEquals(len(gene.children[0].children), 1)

    def test_getItemInterval(self):
        parser = GtfSet(GtfEntryIterator(self.fname))

        genes = parser.fetch('chr1', 500, 1500)
        self.assertEquals(len(genes), 1)
        self.assertEquals(genes[0].name, 'a')

        genes = parser.fetch('chr1', 1500, 5500)
        self.assertEquals(len(genes), 2)
        self.assertEquals(set(gene.name for gene in genes), set('ab'))

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
