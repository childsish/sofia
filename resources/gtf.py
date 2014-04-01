import os

from collections import namedtuple
from modules.gene_model import Gene, Transcript, Exon
from modules.genomic_coordinate import Interval
from modules.indices.interval_index import IntervalIndex
from modules.indices.string_index import StringIndex
from modules.resource import Resource

CHR = 0
SRC = 1
TYPE = 2
START = 3
STOP = 4
SCORE = 5
STRAND = 6
PHASE = 7
ATTR = 8

GtfEntry = namedtuple('GtfEntry', ['chr', 'src', 'type', 'start', 'stop', 'score', 'strand', 'phase', 'attr'])

class GtfParser(Resource):
    
    NAME = 'gtf'
    
    def __init__(self, fname, iname=None):
        super(GtfParser, self).__init__(fname, iname)
        self.parser = GtfFile(fname) if iname is None else\
            IndexedGtfFile(iname)
    
    def __iter__(self):
        return iter(self.parser)
    
    def __getitem__(self, key):
        if hasattr(key, 'chr') and hasattr(key, 'pos') and hasattr(key, 'ref'):
            key = Interval(key.chr, key.pos, key.pos + len(key.ref))
        return self.parser[key]
    
    def index(self, iname):
        os.mkdir(iname)
        self.ivlidx = IntervalIndex(os.path.join(iname, 'ivl.%s'%IntervalIndex.EXT))
        self.stridx = StringIndex(os.path.join(iname, 'str.%s'%StringIndex.EXT))
        infile = open(self.fname)
        while True:
            pos = infile.tell()
            line = infile.readline()
            if line == '': #do-while
                break
            elif line[0] == '#':
                continue
            parts = line.split('\t')
            if parts[TYPE] != 'gene':
                continue
            ivl = Interval(parts[CHR], parts[START], parts[STOP])
            self.ivlidx[ivl] = pos
            attr = self._parseAttributes(parts[ATTR])
            self.stridx[attr.name] = pos

class GtfFile(object):
    def __init__(self, fname):
        self.fname = fname
        self.entries = None
        self.index = None
    
    def __iter__(self):
        return iterModels(self.fname)
    
    def __getitem__(self, key):
        if self.entries is None:
            self.entries = list(iterModels(self.fname))
            self.index = self._createIndex(self.entries)
        return [self.entries[idx] for idx in self.index[key]]
    
    def _createIndex(self, entries):
        index = IntervalIndex()
        for i, entry in enumerate(entries):
            index[entry.ivl] = i
        return index

class IndexedGtfFile(object):
    def __init__(self, fname, iname):
        if iname is not None:
            self.ivlidx = IntervalIndex(os.path.join(iname, 'ivl.%s'%IntervalIndex.EXT))
            self.stridx = StringIndex(os.path.join(iname, 'str.%s'%StringIndex.EXT))
    
    def __iter__(self):
        return iterModels(self.fname)
    
    def __getitem__(self, key):
        infile = open(self.fname)
        if isinstance(key, basestring):
            file_poss = [self.stridx[key]]
        elif hasattr(key, 'start') and hasattr(key, 'stop'):
            file_poss = self.ivlidx[key]
        else:
            msg = 'Can not get models from gtf using this key type: {type}'
            raise TypeError(msg.format(type=type(key)))
        res = []
        for file_pos in file_poss:
            infile.seek(file_pos)
            res.append(self._iterEntries(infile).next())
        infile.close()
        return res
    
def iterModels(fname):
    infile = open(fname)
    gene = None
    for entry in iterEntries(infile):
        ivl = Interval(entry.chr, entry.start, entry.stop)
        if entry.type == 'gene':
            if gene is not None:
                yield gene
            gene = Gene(entry.attr['gene_name'], ivl)
        elif entry.type == 'transcript':
            gene.transcripts[entry.attr['transcript_name']] =\
                Transcript(entry.attr['transcript_name'], ivl)
        elif entry.type in ('exon', 'CDS', 'UTR'):
            gene.transcripts.values()[-1].exons.append(Exon(ivl, entry.type))
        elif entry.type in ('start_codon', 'stop_codon'):
            continue
        else:
            raise TypeError('Unknown type: %s'%entry.type)
    yield gene
    infile.close()

def iterEntries(infile):
    for line in infile:
        if line.startswith('#'):
            continue
        parts = line.split('\t')
        parts[START] = int(parts[START]) - 1
        parts[STOP] = int(parts[STOP])
        parts[ATTR] = parseAttributes(parts[ATTR])
        yield GtfEntry(*parts)

def parseAttributes(attr):
    parts = [part.strip().split(' ', 1) for part in attr.strip().split(';') if part != '']
    for i, part in enumerate(parts):
        if part[1].startswith('"'):
            parts[i][1] = part[1][1:-1]
        else:
            parts[i][1] = int(part[1])
    return dict(parts)
