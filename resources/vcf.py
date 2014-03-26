import os

from collections import namedtuple
from itertools import izip
from modules.resource import Resource
from modules.genomic_coordinate import Interval
from modules.indices.interval_index import IntervalIndex

CHR = 0
POS = 1
ID = 2
REF = 3
ALT = 4
QUAL = 5
FILTER = 6
ATTR = 7
FORMAT = 8

VcfEntry = namedtuple('VcfEntry', ['chr', 'pos', 'id', 'ref', 'alt', 'qual', 'filter', 'attr', 'samples'])

class Vcf(Resource):
    
    NAME = 'vcf'
    
    def __init__(self, fname, iname=None):
        super(Vcf, self).__init__(fname, iname)
        if iname is not None:
            self.ivlidx = IntervalIndex(os.path.join(iname, 'ivl.%s'%IntervalIndex.EXT))
        infile = open(fname)
        self.hdrs = self._parseHeaders(infile)
        infile.close()
        self.samples = [sample.strip() for sample in self.hdrs[-1].split('\t')[FORMAT + 1:]]
    
    def __iter__(self):
        infile = open(self.fname)
        for entry in self._iterEntries(infile):
            yield entry
        infile.close()
    
    def __getitem__(self, key):
        infile = open(self.fname)
        if hasattr(key, 'start') and hasattr(key, 'stop'):
            file_poss = self.ivlidx[key]
        else:
            msg = 'Can not get variants from vcf using this key type: {type}'
            raise TypeError(msg.format(type=type(key)))
        res = []
        for file_pos in file_poss:
            infile.seek(file_pos)
            res.append(self._iterEntries(infile).next())
        infile.close()
        return res
    
    def index(self):
        infile = open(self.location)
        self.parseHeaders(infile)
        while True:
            file_pos = infile.tell()
            parts = infile.readline().strip().split('\t')
            if len(parts) == 0: #do-while
                break
            
            ivl_pos = int(parts[POS]) - 1
            ivl = Interval(parts[CHR], ivl_pos, ivl_pos + len(parts[REF]))
            self.index.insertFilePosition(ivl, file_pos)
        infile.close()
    
    def _iterEntries(self, infile):
        for line in infile:
            if line.startswith('#'):
                continue
            parts = line.split('\t')
            parts[POS] = int(parts[POS]) - 1
            parts[ATTR] = self._parseAttributes(parts[ATTR])
            parts[FORMAT:] = self._parseSamples(parts[FORMAT:])
            yield VcfEntry(*parts)
    
    def _parseHeaders(self, fhndl):
        hdrs = []
        while True:
            line = fhndl.readline().strip()
            if not line.startswith('##'):
                break
            hdrs.append(line)
        hdrs.append(line)
        return hdrs
    
    def _parseSamples(self, parts):
        res = []
        keys = parts[0].split(':')
        for i in xrange(1, len(parts)):
            res.append(dict(izip(keys, parts[i].strip().split(':'))))
        return dict(zip(self.samples, res))
