import os
import pysam

from collections import defaultdict
from binf.genomic_coordinate import Interval
from binf.gene_model import Gene, Transcript, Exon
from iterator import GtfLineIterator, GtfEntityIterator


class IndexedGtfFile(object):
    def __init__(self, fname):
        self.fname = os.path.abspath(fname)
        # kiname = '%s.lhci'%self.fname
        #if not os.path.exists(kiname):
        #    raise ValueError('File missing key index. '\
        #        'Try: python -m lhc.file_formats.gtf index <FILENAME>.')
        #self.key_index = {parts[0]: [parts[1], int(parts[2]), int(parts[3])]\
        #    for parts in (line.strip().split('\t') for line in open(kiname))}
        iiname = '{}.tbi'.format(self.fname)
        if not os.path.exists(iiname):
            raise ValueError('File missing interval index. Try: tabix -p gff <FILENAME>.')
        self.ivl_index = pysam.Tabixfile(self.fname)

    def __getitem__(self, key):
        if isinstance(key, basestring):
            return self.get_gene_by_gene_id(key)
        if hasattr(key, 'chr') and hasattr(key, 'pos') and hasattr(key, 'ref'):
            return self.get_genes_at_position(key.chr, key.pos)
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            return self.get_genes_in_interval(key.chr, key.start, key.stop)
        else:
            raise NotImplementedError('Random access not implemented for {}'.format(type(key)))

    def get_gene_by_gene_id(self, gene_id):
        chr, start, stop = self.key_index[gene_id]
        gene = Gene(gene_id, Interval(chr, start, stop))
        return self._complete_gene(gene)

    def get_genes_at_position(self, chr, pos):
        genes = self._get_gene_intervals_in_interval(chr, pos, pos + 1)
        return [self._complete_gene(gene) for gene in genes]

    def get_genes_in_interval(self, chr, start, stop):
        genes = self._get_gene_intervals_in_interval(chr, start, stop)
        return [self._complete_gene(gene) for gene in genes]

    def _get_gene_intervals_in_interval(self, chr, start, stop):
        lines = [GtfLineIterator.parse(line) for line in self.ivl_index.fetch(chr, start, stop)]
        return [line for line in lines if line.type == 'gene']

    def _complete_gene(self, gene):
        lines = self.ivl_index.fetch(gene.chr, gene.start, gene.stop)
        transcript_exons = defaultdict(list)
        for line in lines:
            type_, ivl, attr = GtfEntityIterator._parse_line(line)
            if attr['gene_name'] != gene.name:
                continue

            if type_ == 'CDS':
                entry = (int(attr['exon_number']), Exon(ivl, 'CDS'))
                transcript_exons[attr['transcript_name']].append(entry)
            elif type_ == 'transcript':
                transcript = Transcript(attr['transcript_name'], ivl)
                gene.transcripts[transcript.name] = transcript
        for transcript, exons in transcript_exons.iteritems():
            gene.transcripts[transcript].exons = [exon for exon_no, exon in sorted(exons)]
        return gene

