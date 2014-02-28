import os

from functools import partial
from lhc.binf.variant import Variant
from lhc.binf.genomic_coordinate import Interval

CHR = 0
START = 1
STOP = 1
ID = 2
REF = 3
ALT1 = 4
ALT2 = 4
QUAL = 5
ATTR = 7

def iterVcf(fname):
    def parseType(ref, alt):
        if len(ref) == 1 and len(alt) == 1:
            return 'SNP'
        elif len(ref) == len(alt):
            return 'MNP'
        elif len(ref) > len(alt):
            return 'DEL'
        elif len(ref) < len(alt):
            return 'INS'
        raise ValueError('Unknown mutation type: %s %s'%(ref, alt))
    
    genotype = os.path.basename(fname.rsplit('.', 1)[0])
    infile = open(fname)
    for line in infile:
        parts = line.split('\t')
        alts = parts[ALT1].split(',')
        ref = parts[REF]
        types = map(partial(parseType, ref=ref), alts)
        yield Variant(Interval(parts[CHR], int(parts[START]) - 1, int(parts[START]) + max(map(len, alts)) - 1),
            alts, types, float(parts[QUAL]), genotype)
    infile.close()
