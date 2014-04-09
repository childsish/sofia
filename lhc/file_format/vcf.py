import argparse
import cPickle
import os

from collections import namedtuple
from itertools import izip
from lhc.file_format.entry_set import EntrySet
from lhc.indices.index import Index
from lhc.indices.exact_key import ExactKeyIndex
from lhc.indices.overlapping_interval import OverlappingIntervalIndex
from lhc.interval import Interval

Variant = namedtuple('Variant', ('chr', 'pos', 'id', 'ref', 'alt', 'qual', 'filter', 'attr', 'samples'))

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
        self.fname = fname
        self.iname = self.getIndexName(fname) if iname is None else iname
        self.pos_index = None
        self.ivl_index = None
        self.data = None
        
        infile = open(fname)
        self.hdrs = self._parseHeaders(infile)
        infile.close()
    
    def __getitem__(self, key):
        if os.path.exists(self.iname):
            if self.pos_index is None:
                infile = open(self.iname)
                self.pos_index = cPickle.load(infile)
                self.ivl_index = cPickle.load(infile)
                infile.close()
            return self._getIndexedData(key)
        elif self.data is None:
            self.pos_index = Index((ExactKeyIndex, ExactKeyIndex))
            self.ivl_index = Index((ExactKeyIndex, OverlappingIntervalIndex))
            self.data = list(iter(self))
            for i, entry in enumerate(self.data):
                self.pos_index[(entry.chr, entry.pos)] = i
                ivl = Interval(entry.pos, entry.pos + len(entry.ref))
                self.ivl_index[(entry.chr, ivl)] = i
        
        if hasattr(key, 'chr') and hasattr(key, 'pos'):
            return self.data[self.pos_index[(key.chr, key.pos)][0].value]
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            return [self.data[v] for k, v in self.ivl_index[(key.chr, key)]]
        raise NotImplementedError('Random access not implemented for %s'%type(key))
    
    def _parseHeaders(self, infile):
        hdrs = []
        line = infile.next().strip()
        while line.startswith('##'):
            hdrs.append(line)
            line = infile.next().strip()
        hdrs.append(line.strip().split('\t'))
        return hdrs
    
    def _iterHandle(self, infile, hdrs=None):
        hdrs = self._parseHeaders(infile) if hdrs is None else hdrs
        if len(hdrs[-1]) <= self.FORMAT:
            return self._iterUnsampledVcf(infile)
        return self._iterSampledVcf(infile, hdrs[-1].split('\t')[self.FORMAT + 1:])

    def _getIndexedData(self, key):
        infile = open(self.fname)
        res = []
        if hasattr(key, 'chr') and hasattr(key, 'pos'):
            fpos = self.pos_index[(key.chr, key.pos)][0]
            infile.seek(fpos.value)
            res = self._iterHandle(infile, self.hdrs).next()
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            fposs = self.ivl_index[(key.chr, key)]
            for fpos in fposs:
                infile.seek(fpos.value)
                res.append(self._iterHandle(infile, self.hdrs).next())
        else:
            raise NotImplementedError('Random access not implemented for %s'%type(key))
        infile.close()
        return res
    
    @classmethod
    def _iterUnsampledVcf(cls, infile):
        for line in infile:
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
    def _iterSampledVcf(cls, infile, sample_names):
        Samples = namedtuple('Samples', sample_names)
        for line in infile:
            parts = line.split('\t')
            yield Variant(parts[cls.CHR],
                int(parts[cls.POS]) - 1,
                parts[cls.ID],
                parts[cls.REF],
                parts[cls.ALT],
                int(parts[cls.QUAL]) if parts[cls.QUAL].isdigit() else parts[cls.QUAL],
                parts[cls.FILTER],
                cls._parseAttributes(parts[cls.ATTR]),
                Samples(*cls._parseSamples(parts)))
    
    @classmethod
    def _parseAttributes(cls, attr_line):
        return dict(attr.split(':') for attr in attr_line.strip().split(','))
    
    @classmethod
    def _parseSamples(cls, parts):
        res = []
        keys = parts[cls.FORMAT].split(':')
        for i in xrange(cls.FORMAT + 1, len(parts)):
            res.append(dict(izip(keys, parts[i].strip().split(':'))))
        return res

def iterEntries(fname):
    parser = VcfParser(fname)
    return iter(parser)

def index(fname, iname=None):
    iname = VcfParser.getIndexName(fname) if iname is None else iname
    outfile = open(iname, 'wb')
    cPickle.dump(_createPosIndex(fname), outfile, cPickle.HIGHEST_PROTOCOL)
    cPickle.dump(_createIvlIndex(fname), outfile, cPickle.HIGHEST_PROTOCOL)
    outfile.close()

def _createPosIndex(fname):
    index = Index((ExactKeyIndex, ExactKeyIndex))
    infile = open(fname, 'rb')
    while True:
        fpos = infile.tell()
        line = infile.readline()
        if line == '':
            break
        elif line.strip() == '' or line.startswith('#'):
            continue
        entry = VcfParser._parseUnsampledLine(line)
        index[(entry.chr, entry.pos)] = fpos
    infile.close()
    return index

def _createIvlIndex(fname):
    index = Index((ExactKeyIndex, OverlappingIntervalIndex))
    infile = open(fname, 'rb')
    while True:
        fpos = infile.tell()
        line = infile.readline()
        if line == '':
            break
        elif line.strip() == '' or line.startswith('#'):
            continue
        entry = VcfParser._parseUnsampledLine(line)
        ivl = Interval(entry.pos, entry.pos + len(entry.ref))
        index[(entry.chr, ivl)] = fpos
    infile.close()
    return index

def main():
    parser = getArgumentParser()
    args = parser.parse_args()
    args.func(args)

def getArgumentParser():
    parser = argparse.ArgumentParser()
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
