import json
import os

from Bio import bgzf
from iterator import GtfLineIterator, GtfEntityIterator
from lhc.io.txt_.index import FileIndex


class IndexedGtfFile(object):
    def __init__(self, fname):
        if not os.path.exists('{}.lci'.format(fname)):
            msg = 'Interval index missing. Try: "python -m lhc.io.bed index {}".'.format(fname)
            raise OSError(msg)
        self.fhndl = bgzf.open(fname)
        fhndl = open('{}.lci'.format(fname))
        self.index = FileIndex.init_from_state(json.load(fhndl))
        fhndl.close()

    def fetch(self, chr, start, stop):
        lines = [GtfLineIterator.parse_line(line) for line in self.ivl_index.fetch(chr, start, stop)]
        return [self.get_gene(line.attr['gene_name'], line) for line in lines if line.type == 'gene']

    def get_gene(self, gene_id, interval=None):
        interval = self.key_index[gene_id] if interval is None else interval
        lines = [GtfLineIterator.parse_line(line)
                 for line in self.ivl_index.fetch(interval.chr, interval.start, interval.stop)]
        return GtfEntityIterator.parse_gene([line for line in lines if line.attr['gene_name'] == gene_id])
