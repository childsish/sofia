import re

class CodonUsageTable:
    
    REGX = re.compile(r'(?P<codon>[ACGU]{3})\s+(?P<frq>\d+\.\d+)\((\s*\d+)\)')
    
    def __init__(self, fname):
        self.cut = self.parseCodonUsageTable(fname)
    
    def __str__(self):
        res = ['%s\t%d'%(codon, value)
            for codon, value in sorted(self.cut.iteritems())]
        return '\n'.join(res)
    
    def __getitem__(self, key):
        return self.cut[key]

    def parseCodonUsageTable(self, fname):
        cut = {}
        infile = open(fname)
        for line in infile:
            matches = CodonUsageTable.REGX.findall(line)
            for match in matches:
                cut[match[0].lower().replace('u', 't')] =\
                    float(match[2])
        infile.close()
        return cut
