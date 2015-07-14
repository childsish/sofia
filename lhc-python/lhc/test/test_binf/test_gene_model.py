import unittest

from lhc.binf.gene_model import Exon, Transcript, Gene
from lhc.binf.genomic_coordinate import GenomicInterval as Interval


class TestGeneModel(unittest.TestCase):
    def test_exon(self):
        seq = {'chr1': 'nnnnnnnnnnaaccggttuunnnnnnnnnn'}

        exon_positive = Exon(Interval('chr1', 10, 20, '+'), 'CDS')
        exon_negative = Exon(Interval('chr1', 10, 20, '-'), 'CDS')

        self.assertEquals('aaccggttuu', exon_positive.get_sub_seq(seq))
        self.assertEquals('aaaaccggtt', exon_negative.get_sub_seq(seq))
        self.assertEquals(0, exon_positive.get_rel_pos(10))
        self.assertEquals(5, exon_positive.get_rel_pos(15))
        self.assertEquals(9, exon_positive.get_rel_pos(19))
        self.assertEquals(9, exon_negative.get_rel_pos(10))
        self.assertEquals(5, exon_negative.get_rel_pos(14))
        self.assertEquals(0, exon_negative.get_rel_pos(19))

    def test_transcript(self):
        seq = {'chr1': (50 * 'n') + (10 * 'a') + (10 * 'n') + (10 * 'c') + (10 * 'n') + (10 * 'g') + (50 * 'n')}

        transcript_positive = Transcript('a', Interval('chr1', 50, 100), [
            Exon(Interval('chr1', 50, 60), 'CDS'),
            Exon(Interval('chr1', 70, 80), 'CDS'),
            Exon(Interval('chr1', 90, 100), 'CDS')
        ])
        transcript_negative = Transcript('b', Interval('chr1', 50, 100, '-'), [
            Exon(Interval('chr1', 50, 60, '-'), 'CDS'),
            Exon(Interval('chr1', 70, 80, '-'), 'CDS'),
            Exon(Interval('chr1', 90, 100, '-'), 'CDS')
        ])

        self.assertEquals('aaaaaaaaaaccccccccccgggggggggg', transcript_positive.get_sub_seq(seq))
        self.assertEquals('ccccccccccggggggggggtttttttttt', transcript_negative.get_sub_seq(seq))
        self.assertEquals(0, transcript_positive.get_rel_pos(50))
        self.assertEquals(9, transcript_positive.get_rel_pos(59))
        self.assertEquals(10, transcript_positive.get_rel_pos(70))
        self.assertEquals(19, transcript_positive.get_rel_pos(79))
        self.assertEquals(20, transcript_positive.get_rel_pos(90))
        self.assertEquals(29, transcript_positive.get_rel_pos(99))

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())