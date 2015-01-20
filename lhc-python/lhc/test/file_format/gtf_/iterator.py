import os
import tempfile
import unittest

from lhc.file_format.gtf_.iterator import GtfLineIterator, GtfEntityIterator


class TestGtf(unittest.TestCase):
    def setUp(self):
        fhndl, self.fname = tempfile.mkstemp()
        self.lines = [
            'chr1\t.\tgene\t1000\t2000\t0\t+\t0\tgene_name "a"',
            'chr1\t.\ttranscript\t1000\t2000\t0\t+\t0\tgene_name "a";transcript_name "a.0"',
            'chr1\t.\tCDS\t1100\t1300\t0\t+\t0\tgene_name "a";transcript_name "a.0"',
            'chr1\t.\tCDS\t1330\t1600\t0\t+\t0\tgene_name "a";transcript_name "a.0"',
            'chr1\t.\tCDS\t1660\t1900\t0\t+\t0\tgene_name "a";transcript_name "a.0"',
            'chr1\t.\ttranscript\t1000\t2000\t0\t+\t0\tgene_name "a";transcript_name "a.1"',
            'chr1\t.\tCDS\t1100\t1300\t0\t+\t0\tgene_name "a";transcript_name "a.1"',
            'chr1\t.\tCDS\t1660\t1900\t0\t+\t0\tgene_name "a";transcript_name "a.1"',
            'chr1\t.\tgene\t5000\t6000\t0\t+\t0\tgene_name "b"',
            'chr1\t.\ttranscript\t5000\t6000\t0\t+\t0\tgene_name "b";transcript_name "b.0"',
            'chr1\t.\tCDS\t5100\t5900\t0\t+\t0\tgene_name "b";transcript_name "b.0"'
        ]
        os.write(fhndl, '\n'.join(self.lines))
        os.close(fhndl)

    def test_parse_attributes(self):
        attr = GtfLineIterator.parse_attributes('gene_name "a"; transcript_name "a.0"; exon 1')

        self.assertEquals(attr['gene_name'], 'a')
        self.assertEquals(attr['transcript_name'], 'a.0')
        self.assertEquals(attr['exon'], 1)

    def test_parse_line(self):
        line = GtfLineIterator.parse_line('chr1\t.\tgene\t1000\t2000\t0\t+\t0\tgene_name "a"\n')

        self.assertEquals(line.chr, 'chr1')
        self.assertEquals(line.start, 999)
        self.assertEquals(line.stop, 2000)
        self.assertEquals(line.strand, '+')
        self.assertEquals(line.attr['gene_name'], 'a')

    def test_parse_gene(self):
        lines = [GtfLineIterator.parse_line(line) for line in self.lines[:8]]

        gene = GtfEntityIterator.parse_gene(lines)

        self.assertEquals('a', gene.name)
        self.assertEquals({'a.0', 'a.1'}, set(gene.transcripts))
        exon = gene.transcripts['a.1'].exons[-1]
        self.assertEquals((1659, 1900), (exon.ivl.start, exon.ivl.stop))

    def test_iter_gtf(self):
        it = GtfEntityIterator(self.fname)
        
        gene = it.next()
        self.assertEquals('a', gene.name)
        self.assertEquals(2, len(gene.transcripts))
        self.assertEquals('a.0', gene.transcripts.values()[0].name)
        self.assertEquals('a.1', gene.transcripts.values()[1].name)
        self.assertEquals(3, len(gene.transcripts.values()[0].exons))
        self.assertEquals(2, len(gene.transcripts.values()[1].exons))
        
        gene = it.next()
        self.assertEquals('b', gene.name)
        self.assertEquals(1, len(gene.transcripts))
        self.assertEquals('b.0', gene.transcripts.values()[0].name)
        self.assertEquals(1, len(gene.transcripts.values()[0].exons))
        
        self.assertRaises(StopIteration, it.next)
    
    def tearDown(self):
        os.remove(self.fname)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
