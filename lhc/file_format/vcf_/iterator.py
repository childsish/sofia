import gzip

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
    INFO = 7
    FORMAT = 8
    
    def __init__(self, fname):
        self.fname = fname
        self.fhndl = gzip.open(fname) if fname.endswith('.gz') else open(fname)
        self.line_no = 0
        self.hdrs = self._parseHeaders()
    
    def __del__(self):
        if hasattr(self, 'fhndl') and not self.fhndl.closed:
            self.fhndl.close()
    
    def __iter__(self):
        return self
    
    def next(self):
        self.line_no += 1
        return self._parseLine(self.fhndl.next())
    
    def seek(self, fpos):
        self.fhndl.seek(fpos)
    
    def _parseHeaders(self):
        fhndl = self.fhndl
        hdrs = OrderedDict()
        line = fhndl.next().strip()
        self.line_no += 1
        if 'VCF' not in line:
            raise ValueError('Invalid VCF file. Line 1: %s'%line.strip())
        while line.startswith('##'):
            key, value = line.split('=', 1)
            if key not in hdrs:
                hdrs[key] = []
            hdrs[key].append(value)
            line = fhndl.next().strip()
            self.line_no += 1
        hdrs['##SAMPLES'] = line.strip().split('\t')[9:]
        return hdrs
    
    def _parseLine(self, line):
        parts = line.strip().split('\t')
        return Variant(parts[self.CHR],
            int(parts[self.POS]) - 1,
            parts[self.ID],
            parts[self.REF],
            parts[self.ALT],
            self._parseQuality(parts[self.QUAL]),
            parts[self.FILTER],
            self._parseAttributes(parts[self.INFO]),
            self._parseSamples(parts))

    def _parseQuality(self, qual):
        if qual == '.':
            return '.'
        try:
            res = float(qual)
        except TypeError:
            return '.'
        return res
    
    def _parseAttributes(self, attr_line):
        return dict(attr.split('=', 1) if '=' in attr else (attr, attr)\
            for attr in attr_line.strip().split(';'))
    
    def _parseSamples(self, parts):
        res = {}
        if self.FORMAT < len(parts):
            keys = parts[self.FORMAT].split(':')
            for i, sample in enumerate(self.hdrs['##SAMPLES']):
                res[sample] = {} if parts[self.FORMAT + i + 1] == '.' else\
                    dict(izip(keys, parts[self.FORMAT + i + 1].strip().split(':')))
        return res

