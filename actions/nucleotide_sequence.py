from sofia_.action import Action

from collections import Counter
from lhc.binf.kmer import KmerCounter


class CalculateKNucleotideFrequency(Action):

    IN = ['nucleotide_sequence']
    OUT = ['nucleotide_frequency']

    def init(self, k=None):
        self.k = k

    def calculate(self, coding_sequence):
        return KmerCounter(coding_sequence, self.k)

    def format(self, nucleotide_frequency):
        return str(nucleotide_frequency)


class NucleotideSkew(Action):

    IN = ['nucleotide_sequence']
    OUT = ['nucleotide_skew']

    def calculate(self, nucleotide_sequence):
        counts = Counter(nucleotide_sequence.lower())
        at_skew = (counts['a'] - counts['t']) / float(counts['a'] + counts['t'])
        gc_skew = (counts['g'] - counts['c']) / float(counts['g'] + counts['c'])
        return {'at_skew': at_skew, 'gc_skew': gc_skew}


class OpenReadingFrames(Action):

    IN = ['nucleotide_sequence']
    OUT = ['open_reading_frame']

    def calculate(self, nucleotide_sequence):
        stops = set(('taa', 'tag', 'tga'))
        res = []
        for i in xrange(len(nucleotide_sequence)):
            if not nucleotide_sequence[i:i + 3] == 'atg':
                continue
            for j in xrange(i, len(nucleotide_sequence), 3):
                if nucleotide_sequence[j:j + 3] in stops:
                    res.append(nucleotide_sequence[i:j + 3])
        return res
