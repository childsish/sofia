import re

from lhc.binf.cut import CodonUsageTable

def readCodonUsageTable(fname):
    REGX = re.compile(r'(?P<codon>[ACGU]{3})\s+(?P<frq>\d+\.\d+)\((\s*\d+)\)')
    cut = CodonUsageTable()
    infile = open(fname)
    for line in infile:
        matches = REGX.findall(line)
        for match in matches:
            cut[match[0].lower().replace('u', 't')] =\
                float(match[2])
    infile.close()
    return cut
