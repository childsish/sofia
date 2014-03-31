import cPickle

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
INFO = 7
FORMAT = 8

class VcfParser(Resource):
    
    NAME = 'vcf'
    
    def __init__(self, fname, iname=None):
        super(VcfParser, self).__init__(fname, iname)
        self.parser = VcfFile(fname) if iname is None else\
            IndexedVcfFile(iname)
    
    def __iter__(self):
        return iter(self.parser)
    
    def __getitem__(self, key):
        return self.parser[key]
    
    def index(self, iname):
        index = IntervalIndex()
        infile = open(self.fname)
        parseHeaders(infile)
        while True:
            file_pos = infile.tell()
            parts = infile.readline().strip().split('\t')
            if len(parts) == 0: #do-while
                break
            
            ivl_pos = int(parts[POS]) - 1
            ivl = Interval(parts[CHR], ivl_pos, ivl_pos + len(parts[REF]))
            self.index.insertFilePosition(ivl, file_pos)
        infile.close()
        outfile = open(iname)
        cPickle.dump(index, outfile)
        outfile.close()

class VcfFile(object):
    def __init__(self, fname):
        self.fname = fname
        self.entries = None
        self.index = None
    
    def __iter__(self):
        return iterEntries(self.fname)
    
    def __getitem__(self, key):
        if self.entries is None:
            self.entries = list(iterEntries(self.fname))
            self.index = self._createIndex(self.entries)
        return [self.entries[idx] for idx in self.index[key]]
    
    def _createIndex(self, entries):
        index = IntervalIndex()
        for i, entry in enumerate(entries):
            ivl = Interval(entry.chr, entry.pos, entry.pos + entry.ref)
            index[ivl] = i
        return index

class IndexedVcfFile(object):
    def __init__(self, fname, iname):
        self.fname = fname
        self.iname = iname
        self.index = None
    
    def __iter__(self):
        infile = open(self.fname)
        for entry in iterEntries(infile):
            yield entry
        infile.close()
    
    def __getitem__(self, key):
        if self.index is None:
            infile = open(self.iname)
            self.index = cPickle.load(infile)
            infile.close()
        if hasattr(key, 'pos') and hasattr(key, 'ref'):
            key = Interval(key.chr, key.pos, key.pos + len(key.ref))
        elif not hasattr(key, 'start') and hasattr(key, 'stop'):
            msg = 'Can not get variants from vcf using this key type: {type}'
            raise TypeError(msg.format(type=type(key)))
        idxs = self.index[key]
        res = []
        infile = open(self.fname)
        for idx in idxs:
            infile.seek(idx)
            res.append(self._iterEntries(infile).next())
        infile.close()
        return res

VcfEntry = namedtuple('VcfEntry', ['chr', 'pos', 'id', 'ref', 'alt', 'qual', 'filter', 'info', 'samples'])
    
def iterEntries(fname):
    infile = open(fname)
    samples = [sample.strip()
        for sample in parseHeaders(infile)[-1].split('\t')[FORMAT + 1:]]
    for line in infile:
        if line.startswith('#'):
            continue
        parts = line.split('\t')
        parts[POS] = int(parts[POS]) - 1
        parts[INFO] = parseInfo(parts[INFO])
        parts[FORMAT:] = [parseSamples(parts[FORMAT:], samples)]
        yield VcfEntry(*parts)
    infile.close()

def parseHeaders(infile):
    hdrs = []
    while True:
        line = infile.readline().strip()
        if not line.startswith('##'):
            break
        hdrs.append(line)
    hdrs.append(line)
    return hdrs

def parseInfo(info):
    return dict(part.split('=') for part in info.split(';'))\
        if '=' in info else {}

def parseSamples(parts, samples):
    res = []
    keys = parts[0].split(':')
    for i in xrange(1, len(parts)):
        res.append(dict(izip(keys, parts[i].strip().split(':'))))
    return dict(zip(samples, res))
