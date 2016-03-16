from iterator import GtfEntryIterator, GtfLineIterator


class IndexedGtfFile(object):
    def __init__(self, index, max_buffer=10):
        self.index = index
        self.buffer = {}
        self.max_buffer = max_buffer

    def fetch(self, chr, start, stop):
        lines = [GtfLineIterator.parse_line(line) for line in self.index.fetch(chr, start, stop)]
        return [self.get_features(line) for line in lines if line.type == 'gene']

    def get_features(self, gene_line):
        buffer_key = gene_line.attr['gene_name']
        if buffer_key in self.buffer:
            return self.buffer[buffer_key]

        genes = GtfEntryIterator.get_features(self.index.fetch(gene_line.chr, gene_line.start, gene_line.stop))
        for gene in genes:
            if gene.name == gene_line.attr['gene_name']:
                if len(self.buffer) > self.max_buffer:
                    self.buffer.popitem()
                self.buffer[buffer_key] = gene
                return gene
        raise KeyError('{}'.format(gene_line.attr['gene_name']))
