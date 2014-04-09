import argparse
import cPickle
import os

from collections import namedtuple
from lhc.binf.genomic_coordinate import Interval
from lhc.binf.gene_model import Gene, Transcript, Exon
from lhc.file_format.entry_set import EntrySet
from lhc.indices.index import Index
from lhc.indices.exact_key import ExactKeyIndex
from lhc.indices.overlapping_interval import OverlappingIntervalIndex

GtfEntry = namedtuple('GtfEntry', ('chr', 'src', 'type', 'start', 'stop',
    'score', 'strand', 'phase', 'attr'))

class GtfParser(EntrySet):
    
    CHR = 0
    SRC = 1
    TYPE = 2
    START = 3
    STOP = 4
    SCORE = 5
    STRAND = 6
    PHASE = 7
    ATTR = 8
    
    def __init__(self, fname, iname=None):
        self.fname = fname
        self.iname = self.getIndexName(fname) if iname is None else iname
        self.key_index = None
        self.ivl_index = None
        self.data = None
    
    def __getitem__(self, key):
        if os.path.exists(self.iname):
            if self.key_index is None:
                infile = open(self.iname)
                self.key_index = cPickle.load(infile)
                self.ivl_index = cPickle.load(infile)
                infile.close()
            return self._getIndexedData(key)
        elif self.data is None:
            self.key_index = ExactKeyIndex()
            self.ivl_index = Index((ExactKeyIndex, OverlappingIntervalIndex))
            self.data = list(iter(self))
            for i, entry in enumerate(self.data):
                self.key_index[entry.name] = i
                self.ivl_index[(entry.ivl.chr, entry.ivl)] = i
        
        if isinstance(key, basestring):
            return self.data[self.key_index[key]]
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            return [self.data[v] for k, v in self.ivl_index[(key.chr, key)]]
        raise NotImplementedError('Random access not implemented for %s'%type(key))

    def _iterHandle(self, infile):
        gene = None
        for line in self._iterLines(infile):
            ivl = Interval(line.chr, line.start, line.stop, line.strand)
            if line.type == 'gene':
                if gene is not None:
                    yield gene
                gene = Gene(line.attr['gene_name'], ivl)
            elif line.type == 'transcript':
                gene.transcripts[line.attr['transcript_name']] =\
                    Transcript(line.attr['transcript_name'], ivl)
            elif line.type == 'CDS':
                gene.transcripts.values()[-1].exons.append(Exon(ivl, 'CDS'))
        yield gene

    def _iterLines(self, infile):
        for line in infile:
            if line.startswith('#') or line.strip() == '':
                continue
            yield self._parseLine(line)

    def _getIndexedData(self, key):
        infile = open(self.fname)
        res = []
        if isinstance(key, basestring):
            fpos = self.key_index[key]
            infile.seek(fpos)
            res = self._iterHandle(infile).next()
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            fposs = self.ivl_index[(key.chr, key)]
            for fpos in fposs:
                infile.seek(fpos.value)
                res.append(self._iterHandle(infile).next())
        else:
            raise NotImplementedError('Random access not implemented for %s'%type(key))
        infile.close()
        return res
    
    @classmethod
    def _parseLine(cls, line):
        parts = line.split('\t')
        parts[cls.START] = int(parts[cls.START]) - 1
        parts[cls.STOP] = int(parts[cls.STOP])
        parts[cls.ATTR] = cls._parseAttributes(parts[cls.ATTR])
        return GtfEntry(*parts)
    
    @classmethod
    def _parseAttributes(cls, attr):
        parts = [part.strip().split(' ', 1)
            for part in attr.split(';')
            if part.strip() != '']
        for i in xrange(len(parts)):
            if parts[i][1].startswith('"'):
                parts[i][1] = parts[i][1][1:-1]
            else:
                parts[i][1] = int(parts[i][1])
        return dict(parts)

def iterEntries(fname):
    parser = GtfParser(fname)
    return iter(parser)

def index(fname, iname=None):
    iname = GtfParser.getIndexName(fname) if iname is None else iname
    outfile = open(iname, 'wb')
    cPickle.dump(_createKeyIndex(fname), outfile, cPickle.HIGHEST_PROTOCOL)
    cPickle.dump(_createIvlIndex(fname), outfile, cPickle.HIGHEST_PROTOCOL)
    outfile.close()

def _createKeyIndex(fname):
    index = ExactKeyIndex()
    infile = open(fname, 'rb')
    while True:
        fpos = infile.tell()
        line = infile.readline()
        if line == '':
            break
        elif line.startswith('#') or line.strip() == '':
            continue
        entry = GtfParser._parseLine(line)
        if entry.type == 'gene':
            index[entry.attr['gene_name']] = fpos
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
        elif line.startswith('#') or line.strip() == '':
            continue
        entry = GtfParser._parseLine(line)
        if entry.type == 'gene':
            ivl = Interval(entry.start, entry.stop)
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
