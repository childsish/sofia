__author__ = 'Liam Childs'

from genomic_interval import GenomicInterval


class GenomicPosition(object):

    def __init__(self, chromosome, position, strand='+'):
        self.chr = chromosome
        self.pos = position
        self.strand = strand

    def __str__(self):
        return '{}:{}'.format(self.chr, self.pos + 1)

    def __eq__(self, other):
        return self.chr == other.chr and self.pos == other.pos and\
            self.strand == other.strand

    def __lt__(self, other):
        return (self.chm < other.chm) or\
            (self.chm == other.chm) and (self.pos < other.pos)

    def get_offset(self, pos):
        return GenomicPosition(self.chr,
                               self.pos + pos if self.strand == '+' else self.pos - pos,
                               self.strand)

    def get_interval(self, pos):
        if isinstance(pos, GenomicPosition):
            if pos.chr != self.chr or pos.strand != self.strand:
                raise ValueError('Positions not on same strand or chromosome: {} vs. {}'.format(self, pos))
            pos = pos.pos
        return GenomicInterval(self.chr, self.pos, pos, self.strand)
