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

class Gtf(Resource):
    
    NAME = 'gtf'
    
    def __init__(self, fname, iname=None):
        super(Gtf, self).__init__(fname, iname)
        if iname is not None:
            self.ivlidx = IntervalIndex(os.path.join(iname, 'ivl.%s'%IntervalIndex.EXT))
            self.stridx = StringIndex(os.path.join(iname, 'str.%s'%StringIndex.EXT))
    
    def __iter__(self):
        infile = open(self.fname)
        for gene in self._iterModels(infile):
            yield gene
        infile.close
    
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
    
    def _iterModels(self, infile):
        gene = None
        for entry in self._iterEntries(infile):
            ivl = Interval(entry.chr, entry.start, entry.stop)
            if entry.type == 'gene':
                if gene is not None:
                    yield gene
                gene = Gene(entry.attr['gene_name'], ivl)
            elif entry.type == 'transcript':
                gene.transcripts[entry.attr['transcript_name']] =\
                    Transcript(entry.attr['transcript_name'], ivl)
            elif entry.type == 'exon':
                gene.transcripts.values[-1].exons.append(Exon(ivl, 'CDS'))
            else:
                raise TypeError('Unknown type: %s'%entry.type)
        yield gene
    
    def _iterEntries(self, infile):
        for line in infile:
            if line.startswith('#'):
                continue
            parts = line.split('\t')
            parts[START] = int(parts[START]) - 1
            parts[STOP] = int(parts[STOP])
            parts[ATTR] = self._parseAttributes(parts[ATTR])
            yield GtfEntry(*parts)
    
    def _parseAttributes(self, attr):
        parts = [part.strip().split(' ', 1) for part in attr.split(';') if part != '']
        for i in xrange(len(parts)):
            if parts[i][1].startswith('"'):
                parts[i][1] = parts[i][1][1:-1]
            else:
                parts[i][1] = int(parts[i][1])
        return dict(parts)
    
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
