import os
import pysam

from collections import defaultdict
from lhc.binf.genomic_coordinate import Interval
from lhc.binf.gene_model import Gene, Transcript, Exon
from lhc.file_format.gtf_.iterator import GtfIterator
    
class IndexedGtfFile(object):
    def __init__(self, fname):
        self.fname = os.path.abspath(fname)
        #kiname = '%s.lhci'%self.fname
        #if not os.path.exists(kiname):
        #    raise ValueError('File missing key index. '\
        #        'Try: python -m lhc.file_formats.gtf index <FILENAME>.')
        #self.key_index = {parts[0]: [parts[1], int(parts[2]), int(parts[3])]\
        #    for parts in (line.strip().split('\t') for line in open(kiname))}
        iiname = '%s.tbi'%self.fname
        if not os.path.exists(iiname):
            raise ValueError('File missing interval index. '\
                'Try: tabix -p gff <FILENAME>.')
        self.ivl_index = pysam.Tabixfile(self.fname)
    
    def __getitem__(self, key):
        if isinstance(key, basestring):
            return self.getGeneByGeneId(key)
        if hasattr(key, 'chr') and hasattr(key, 'pos') and hasattr(key, 'ref'):
            return self.getGenesAtPosition(key.chr, key.pos)
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            return self.getGenesInInterval(key.chr, key.start, key.stop)
        else:
            raise NotImplementedError('Random access not implemented for %s'%type(key))

    def getGeneByGeneId(self, gene_id):
        chr, start, stop = self.key_index[gene_id]
        gene = Gene(gene_id, Interval(chr, start, stop))
        return self._completeGene(gene)

    def getGenesAtPosition(self, chr, pos):
        genes = self._getGeneIntervalsInInterval(chr, pos, pos + 1)
        return [self._completeGene(gene) for gene in genes]
    
    def getGenesInInterval(self, chr, start, stop):
        genes = self._getGeneIntervalsInInterval(chr, start, stop)
        return [self._completeGene(gene) for gene in genes]
    
    def _getGeneIntervalsInInterval(self, chr, start, stop):
        idx = self.ivl_index
        lines = [GtfIterator._parseLine(line) for line in\
            idx.fetch(chr, start, stop)]
        return [(attr['gene_name'], ivl.start, ivl.stop) for type, ivl, attr in lines if type == 'gene']
        genes = [Gene(attr['gene_name'], ivl) for type, ivl, attr in lines\
            if type == 'gene']
        return genes
    
    def _completeGene(self, gene):
        lines = self.ivl_index.fetch(gene.ivl.chr, gene.ivl.start,
            gene.ivl.stop)
        transcripts = {}
        transcript_exons = defaultdict(list)
        for line in lines:
            type_, ivl, attr = GtfIterator._parseLine(line)
            if attr['gene_name'] != gene.name:
                continue
            
            if type_ == 'CDS':
                entry = (int(attr['exon_number']), Exon(ivl, 'CDS'))
                transcript_exons[attr['transcript_name']].append(entry)
            elif type_ == 'transcript':
                transcript = Transcript(attr['transcript_name'], ivl)
                gene.transcripts[transcript.name] = transcript
        for transcript, exons in transcript_exons.iteritems():
            gene.transcripts[transcript].exons = [exon for exon_no, exon in\
                sorted(exons)]
        return gene
