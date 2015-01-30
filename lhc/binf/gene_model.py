from collections import OrderedDict
from lhc.collections.sorted_list import SortedList


class Gene(object):
    def __init__(self, name='', ivl=None, transcripts=None):
        self.name = name
        self.ivl = ivl
        self.transcripts = OrderedDict() if transcripts is None else transcripts

    def get_major_transcript(self):
        return sorted(self.transcripts.itervalues(), key=lambda transcript: len(transcript))[-1]

    def __str__(self):
        return '{}:{}'.format(self.name, str(self.ivl))


class Transcript(object):
    def __init__(self, name, ivl, exons=None):
        self.name = name
        self.ivl = ivl
        self.exons = SortedList(exons, key=lambda x: x.ivl.start)

    def __str__(self):
        return '{}:{}'.format(self.name, str(self.ivl))
    
    def __len__(self):
        return sum(map(len, self.exons))

    def add_exon(self, exon):
        self.exons.add(exon)

    def get_rel_pos(self, pos):
        rel_pos = 0
        it = iter(self.exons) if self.ivl.strand == '+' else reversed(self.exons)
        for exon in it:
            if exon.ivl.start <= pos < exon.ivl.stop:
                return rel_pos + exon.get_rel_pos(pos)
            rel_pos += len(exon)
        raise ValueError('Position outside interval bounds.')
    
    def get_sub_seq(self, seq, fr=None, to=None, valid_types={'CDS', 'UTR5', 'UTR3'}):
        it = iter(self.exons) if self.ivl.strand == '+' else reversed(self.exons)
        return ''.join([exon.get_sub_seq(seq, fr, to) for exon in it if exon.type in valid_types])


class Exon(object):
    def __init__(self, ivl, type_):
        self.ivl = ivl
        self.type = type_
    
    def __str__(self):
        return '{}..{}'.format(self.ivl.start, self.ivl.stop)
    
    def __len__(self):
        return len(self.ivl)
    
    def get_sub_seq(self, seq, fr=None, to=None):
        return self.ivl.get_sub_seq(seq, fr, to)

    def get_rel_pos(self, pos):
        return self.ivl.get_rel_pos(pos)
