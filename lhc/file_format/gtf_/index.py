import os
import pysam

from collections import defaultdict
from operator import add
from lhc.binf.genomic_coordinate import Interval
from lhc.binf.gene_model import Gene, Transcript, Exon
from lhc.file_format.gtf_.iterator import GtfIterator
    
class IndexedGtfFile(object):
    def __init__(self, iname):
        self.iname = iname
        self.fname = os.path.abspath(iname)[:-4]
        self.key_index = {parts[0]: parts[1:] for parts in\
            (line.strip().split('\t') for line in open('%s.lhci'%self.fname))}
        self.ivl_index = pysam.Tabixfile(self.fname)
        
        self.prv_key = None
        self.prv_value = None
    
    def __getitem__(self, key):
        if isinstance(key, basestring):
            ivls = [self.key_index[key]]
        elif hasattr(key, 'chr') and hasattr(key, 'pos') and hasattr(key, 'ref'):
            ivls = self._getGeneIntervalsInInterval(key.chr, key.pos, key.pos + len(key.ref))
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            ivls = self._getGeneIntervalsInInterval(key.chr, key.start, key.stop)
        else:
            raise NotImplementedError('Random access not implemented for %s'%type(key))
        
        return reduce(add, (self._getGenesInInterval(chr, start, stop) for chr, start, stop in ivls))
    
    def _getGeneIntervalsInInterval(self, chr, start, stop):
        return [(chr, int(parts[GtfIterator.START]) - 1, int(parts[GtfIterator.STOP])) for parts in\
            (line.split('\t') for line in self.ivl_index.fetch(chr, start, stop)) if parts[GtfIterator.TYPE] == 'gene']
    
    def _getGenesInInterval(self, chr, start, stop):
        lines = self.ivl_index.fetch(chr, start, stop)
        genes = {}
        gene_transcripts = defaultdict(list)
        transcripts = {}
        transcript_exons = defaultdict(list)
        for line in lines:
            type, ivl, attr = GtfIterator._parseLine(line)
            if type == 'CDS':
                transcript_exons.append(Exon(ivl, 'CDS'))
            elif type == 'transcript':
                transcript = Transcript(attr['transcript_name'], ivl)
                transcripts[transcript.name] = transcript
                gene_transcripts[transcript.name] = transcript
            elif type == 'gene':
                genes[attr['gene_name']] = Gene(attr['gene_name'], ivl)
        for transcript, exons in transcript_exons.iteritems():
            transcripts[transcript].exons = exons
        for gene, transcripts in gene_transcripts.iteritems():
            genes[gene].transcripts = {transcript.name: transcript for transcript in transcripts}
        return genes
