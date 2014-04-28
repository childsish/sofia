import argparse
import cPickle
import os

from collections import namedtuple
from lhc.binf.genomic_coordinate import Interval as GenomicInterval
from lhc.binf.gene_model import Gene, Transcript, Exon
from lhc.file_format.entry_set import EntrySet
from lhc.indices.index import Index
from lhc.indices.exact_key import ExactKeyIndex
from lhc.indices.overlapping_interval import OverlappingIntervalIndex
from lhc.interval import Interval

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
        super(GtfParser, self).__init__(fname, iname)
        self.key_index = None
        self.ivl_index = None
        self.prv_fposs = None
        self.prv_res = None
    
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
        elif hasattr(key, 'chr') and hasattr(key, 'pos') and hasattr(key, 'ref'):
            ivl = Interval(key.pos, key.pos + len(key.ref))
            return [self.data[v] for k, v in self.ivl_index[(key.chr, ivl)]]
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            return [self.data[v] for k, v in self.ivl_index[(key.chr, key)]]
        raise NotImplementedError('Random access not implemented for %s'%type(key))

    def _iterHandle(self, infile):
        gene = None
        for line in self._iterLines(infile):
            ivl = GenomicInterval(line.chr, line.start, line.stop, line.strand)
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
        if isinstance(key, basestring):
            fposs = [self.key_index[key]]
            return self._getEntryAtFilePosition(fposs)[0]
        elif hasattr(key, 'chr') and hasattr(key, 'pos') and hasattr(key, 'ref'):
            ivl = Interval(key.pos, key.pos + len(key.ref))
            fposs = self.ivl_index[(key.chr, ivl)]
            return self._getEntryAtFilePosition(fposs)
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            fposs = self.ivl_index[(key.chr, key)]
            return self._getEntryAtFilePosition(fposs)
        raise NotImplementedError('Random access not implemented for %s'%type(key))
    
    def _getEntryAtFilePosition(self, fposs):
        """Get the entry at the given positions
        
        Accessing the gene models is usually done sequentially over the
        chromosome. Because of this, the requested file position is checked
        to see if it accessed previously. This avoids calling the expensive
        funcion _parseAttributes.
        
        :param fposs: the file positions to get the GTF entries from
        :type fposs: list of int
        """
        if fposs == self.prv_fposs:
            return self.prv_res
        else:
            self.prv_fposs = fposs
        
        res = []
        for fpos in fposs:
            self.fhndl.seek(fpos.value)
            res.append(self._iterHandle(self.fhndl).next())
        
        self.prv_res = res
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
        parts = (part.strip() for part in attr.split(';'))
        parts = [part.split(' ', 1) for part in parts if part != '']
        for part in parts:
            part[1] = part[1][1:-1] if part[1].startswith('"') else int(part[1])
        return dict(parts)

def iterEntries(fname):
    parser = GtfParser(fname)
    return iter(parser)

def index(fname, iname=None):
    iname = GtfParser.getIndexName(fname) if iname is None else iname
    key_index, ivl_index = _createIndices(fname)
    outfile = open(iname, 'wb')
    cPickle.dump(key_index, outfile, cPickle.HIGHEST_PROTOCOL)
    cPickle.dump(ivl_index, outfile, cPickle.HIGHEST_PROTOCOL)
    outfile.close()

def _createIndices(fname):
    key_index = ExactKeyIndex()
    ivl_index = Index((ExactKeyIndex, OverlappingIntervalIndex))
    infile = open(fname, 'rb')
    fpos = 0
    for line in infile:
        if line.startswith('#') or line.strip() == '':
            fpos += len(line)
            continue
        entry = GtfParser._parseLine(line)
        if entry.type == 'gene':
            key_index[entry.attr['gene_name']] = fpos
            ivl = Interval(entry.start, entry.stop)
            ivl_index[(entry.chr, ivl)] = fpos
        fpos += len(line)
    infile.close()
    return key_index, ivl_index

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
