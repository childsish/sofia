import argparse
import cPickle
import gzip
import os

from collections import namedtuple
from itertools import izip
from lhc.collection.sorted_dict import SortedDict
from lhc.file_format.entry_set import EntrySet
from lhc.indices.index import Index
from lhc.indices.exact_key import ExactKeyIndex
from lhc.indices.overlapping_interval import OverlappingIntervalIndex
from lhc.interval import Interval
from numpy.core.fromnumeric import sort

Variant = namedtuple('Variant', ('chr', 'pos', 'id', 'ref', 'alt', 'qual', 'filter', 'attr', 'samples'))

def iterEntries(fname):
    parser = VcfParser(fname)
    return iter(parser)

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
        return self._iterSampledVcf(infile, hdrs[-1][self.FORMAT + 1:])

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

def index(fname, iname=None):
    iname = VcfParser.getIndexName(fname) if iname is None else iname
    outfile = open(iname, 'wb')
    pos_index, ivl_index = _createIndices(fname)
    cPickle.dump(pos_index, outfile, cPickle.HIGHEST_PROTOCOL)
    cPickle.dump(ivl_index, outfile, cPickle.HIGHEST_PROTOCOL)
    outfile.close()

def _createIndices(fname):
    pos_index = Index((ExactKeyIndex, ExactKeyIndex))
    ivl_index = Index((ExactKeyIndex, OverlappingIntervalIndex))
    infile = open(fname, 'rb')
    chr = None
    while True:
        fpos = infile.tell()
        line = infile.readline()
        if line == '':
            break
        elif line.strip() == '' or line.startswith('#'):
            continue
        entry = VcfParser._parseUnsampledLine(line)
        pos_index[(entry.chr, entry.pos)] = fpos
        ivl = Interval(entry.pos, entry.pos + len(entry.ref))
        ivl_index[(entry.chr, ivl)] = fpos
        if entry.chr != chr:
            print entry.chr
            chr = entry.chr
    infile.close()
    return pos_index, ivl_index

def merge(fnames):
    infiles = [gzip.open(fname) if fname.endswith('gz') else open(fname) for fname in fnames]
    tops = [infile.next().strip().split('\t') for infile in infiles]
    while '#' in [top[0][0] for top in tops]:
        for i in xrange(len(tops)):
            if tops[i][0][0] == '#':
                tops[i] = infiles[i].next().strip().split('\t')
    sorted_tops = _initSorting(tops)
    
    print '#CHR\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tATTR\tFORMAT\t' + '\t'.join(fnames)
    while len(sorted_tops) > 0:
        key, idxs = sorted_tops.popLowest()
        entry = tops[idxs[0]]
        print '\t'.join(entry[:9]) + '\t' + '\t'.join('\t'.join(tops[idx][9:]) for idx in idxs)
        for idx in idxs:
            try:
                tops[idx] = infiles[idx].next().strip().split('\t')
                _updateSorting(sorted_tops, tops[idx], idx)
            except StopIteration:
                pass

def _initSorting(tops):
    sorted_tops = SortedDict()
    for idx, entry in enumerate(tops):
        _updateSorting(sorted_tops, entry, idx)
    return sorted_tops

def _updateSorting(sorted_tops, entry, idx):
    key = (entry[0], entry[1])
    if key not in sorted_tops:
        sorted_tops[key] = []
    sorted_tops[key].append(idx)

def main():
    parser = getArgumentParser()
    args = parser.parse_args()
    args.func(args)

def getArgumentParser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    index_parser = subparsers.add_parser('index')
    index_parser.add_argument('input')
    index_parser.set_defaults(func=lambda args:index(args.input))
    
    merge_parser = subparsers.add_parser('merge')
    merge_parser.add_argument('inputs', nargs='+')
    merge_parser.set_defaults(func=lambda args: merge(args.inputs))
    
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
