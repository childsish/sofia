import cPickle
import os

from collections import namedtuple, OrderedDict
from itertools import izip
from lhc.binf.genomic_coordinate import Interval
from lhc.file_format.entry_set import EntrySet
from lhc.indices.index import Index
from lhc.indices.exact_key import ExactKeyIndex
from lhc.indices.overlapping_interval import OverlappingIntervalIndex

Variant = namedtuple('Variant', ('chr', 'pos', 'id', 'ref', 'alt', 'qual', 'filter', 'info', 'samples'))

class VcfParser(EntrySet):

    CHR = 0
    POS = 1
    ID = 2
    REF = 3
    ALT = 4
    QUAL = 5
    FILTER = 6
    ATTR = 7
    FORMAT = 8
    
    def __init__(self, fname, iname=None):
        super(VcfParser, self).__init__(fname, iname)
        self.pos_index = None
        self.ivl_index = None
        
        fhndl = open(fname)
        self.hdrs = self._parseHeaders(fhndl)
        fhndl.close()
    
    def __getitem__(self, key):
        if os.path.exists(self.iname):
            if self.pos_index is None:
                fhndl = open(self.iname)
                self.pos_index = cPickle.load(fhndl)
                self.ivl_index = cPickle.load(fhndl)
                fhndl.close()
            return self._getIndexedData(key)
        elif self.data is None:
            self.pos_index = Index((ExactKeyIndex, ExactKeyIndex))
            self.ivl_index = Index((ExactKeyIndex, OverlappingIntervalIndex))
            self.data = list(iter(self))
            for i, entry in enumerate(self.data):
                self.pos_index[(entry.chr, entry.pos)] = i
                ivl = Interval(entry.chr, entry.pos, entry.pos + len(entry.ref))
                self.ivl_index[(entry.chr, ivl)] = i
        
        if hasattr(key, 'chr') and hasattr(key, 'pos'):
            return self.data[self.pos_index[(key.chr, key.pos)]]
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            return [self.data[v] for k, v in self.ivl_index[(key.chr, key)]]
        raise NotImplementedError('Random access not implemented for %s'%type(key))
    
    def _iterHandle(self, fhndl, hdrs=None):
        hdrs = self._parseHeaders(fhndl) if hdrs is None else hdrs
        if len(hdrs['##SAMPLES']) > 0:
            return self._iterSampledVcf(fhndl, hdrs['##SAMPLES'])
        return self._iterUnsampledVcf(fhndl)

    def _getIndexedData(self, key):
        res = []
        if hasattr(key, 'chr') and hasattr(key, 'pos'):
            fpos = self.pos_index[(key.chr, key.pos)][0]
            self.fhndl.seek(fpos.value)
            res = self._iterHandle(self.fhndl, self.hdrs).next()
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            fposs = self.ivl_index[(key.chr, key)]
            for fpos in fposs:
                self.fhndl.seek(fpos.value)
                res.append(self._iterHandle(self.fhndl, self.hdrs).next())
        else:
            raise NotImplementedError('Random access not implemented for %s'%type(key))
        return res
    
    @classmethod
    def _parseHeaders(cls, fhndl):
        hdrs = OrderedDict()
        line = fhndl.next().strip()
        while line.startswith('##'):
            key, value = line.split('=', 1)
            if key not in hdrs:
                hdrs[key] = []
            hdrs[key].append(value)
            line = fhndl.next().strip()
        hdrs['##SAMPLES'] = line.strip().split('\t')[9:]
        return hdrs
    
    @classmethod
    def _iterUnsampledVcf(cls, fhndl):
        for line in fhndl:
            yield cls._parseUnsampledLine(line)
    
    @classmethod
    def _parseUnsampledLine(cls, line):
        parts = line.split('\t')
        return Variant(parts[cls.CHR],
            int(parts[cls.POS]) - 1,
            parts[cls.ID],
            parts[cls.REF],
            parts[cls.ALT],
            int(parts[cls.QUAL]) if parts[cls.QUAL].isdigit() else parts[cls.QUAL],
            parts[cls.FILTER],
            cls._parseAttributes(parts[cls.ATTR]),
            None)
    
    @classmethod
    def _iterSampledVcf(cls, fhndl, sample_names):
        for line in fhndl:
            parts = line.split('\t')
            yield Variant(parts[cls.CHR],
                int(parts[cls.POS]) - 1,
                parts[cls.ID],
                parts[cls.REF],
                parts[cls.ALT],
                int(parts[cls.QUAL]) if parts[cls.QUAL].isdigit() else parts[cls.QUAL],
                parts[cls.FILTER],
                cls._parseAttributes(parts[cls.ATTR]),
                dict(izip(sample_names, cls._parseSamples(parts))))
    
    @classmethod
    def _parseAttributes(cls, attr_line):
        return dict(attr.split('=', 1) if '=' in attr else (attr, attr)\
            for attr in attr_line.strip().split(';'))
    
    @classmethod
    def _parseSamples(cls, parts):
        res = []
        keys = parts[cls.FORMAT].split(':')
        for i in xrange(cls.FORMAT + 1, len(parts)):
            res.append(dict(izip(keys, parts[i].strip().split(':'))))
        return res
