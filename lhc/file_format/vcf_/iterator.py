from collections import OrderedDict, namedtuple
from itertools import izip

Variant = namedtuple('Variant', ('chr', 'pos', 'id', 'ref', 'alt', 'qual', 'filter', 'info', 'samples'))

class VcfIterator(object):

    CHR = 0
    POS = 1
    ID = 2
    REF = 3
    ALT = 4
    QUAL = 5
    FILTER = 6
    ATTR = 7
    FORMAT = 8
    
    def __init__(self, fname):
        self.fname = fname
        
        fhndl = open(fname)
        self.hdrs = self._parseHeaders()
        fhndl.close()
    
    def __iter__(self):
        fhndl = open(self.fname)
        line = fhndl.next()
        while line.startswith('##'):
            line = fhndl.next()
        for line in fhndl:
            parts = line.strip().split('\t')
            yield Variant(parts[self.CHR],
                int(parts[self.POS]) - 1,
                parts[self.ID],
                parts[self.REF],
                parts[self.ALT],
                int(parts[self.QUAL]) if parts[self.QUAL].isdigit() else parts[self.QUAL],
                parts[self.FILTER],
                self._parseAttributes(parts[self.ATTR]),
                self._parseSamples(parts))
        fhndl.close()

    def _parseHeaders(self):
        fhndl = open(self.fname)
        hdrs = OrderedDict()
        line = fhndl.next().strip()
        if not 'VCF' in line:
            raise ValueError('Invalid VCF file. Line 1: %s'%line.strip())
        while line.startswith('##'):
            key, value = line.split('=', 1)
            if key not in hdrs:
                hdrs[key] = []
            hdrs[key].append(value)
            line = fhndl.next().strip()
        hdrs['##SAMPLES'] = line.strip().split('\t')[9:]
        return hdrs
    
    def _parseAttributes(self, attr_line):
        return dict(attr.split('=', 1) if '=' in attr else (attr, attr)\
            for attr in attr_line.strip().split(';'))
    
    def _parseSamples(self, parts):
        res = OrderedDict()
        keys = parts[self.FORMAT].split(':')
        for i, sample in enumerate(self.hdrs['##SAMPLES']):
            res[sample] = dict(izip(keys, parts[self.FORMAT + i + 1].strip().split(':')))
        return res
