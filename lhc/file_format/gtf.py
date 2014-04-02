from collections import namedtuple
from lhc.binf.genomic_coordinate import Interval
from lhc.binf.gene_model import Gene, Transcript, Exon

CHR = 0
SRC = 1
TYPE = 2
START = 3
STOP = 4
SCORE = 5
STRAND = 6
PHASE = 7
ATTR = 8

def iterModels(fname):
    gene = None
    for entry in iterEntries(fname):
        ivl = Interval(entry.chr, entry.start, entry.stop, entry.strand)
        if entry.type == 'gene':
            if gene is not None:
                yield gene
            gene = Gene(entry.attr['gene_name'], ivl)
        elif entry.type == 'transcript':
            gene.transcripts[entry.attr['transcript_name']] =\
                Transcript(entry.attr['transcript_name'], ivl)
        elif entry.type == 'CDS':
            gene.transcripts.values()[-1].exons.append(Exon(ivl, 'CDS'))
        
GtfEntry = namedtuple('GtfEntry', ('chr', 'src', 'type', 'start', 'stop',
    'score', 'strand', 'phase', 'attr'))
def iterEntries(fname):
    infile = open(fname)
    for line in infile:
        if line.startswith('#'):
            continue
        parts = line.split('\t')
        parts[START] = int(parts[START]) - 1
        parts[STOP] = int(parts[STOP])
        parts[ATTR] = parseAttributes(parts[ATTR])
        yield GtfEntry(*parts)
    infile.close()

def parseAttributes(attr):
    parts = [part.strip().split(' ', 1)
        for part in attr.split(';')
        if part.strip() != '']
    for i in xrange(len(parts)):
        if parts[i][1].startswith('"'):
            parts[i][1] = parts[i][1][1:-1]
        else:
            parts[i][1] = int(parts[i][1])
    return dict(parts)

