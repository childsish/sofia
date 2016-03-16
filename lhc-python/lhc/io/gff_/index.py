from iterator import GffEntryIterator, GffLineIterator


class IndexedGffFile(object):
    def __init__(self, index, max_buffer=10):
        self.index = index
        self.buffer = {}
        self.max_buffer = max_buffer

    def fetch(self, chr, start, stop=None):
        if stop is None:
            stop = start + 1
        lines = [GffLineIterator.parse_line(line) for line in self.index.fetch(chr, start, stop)]
        return [self.get_features(line) for line in lines if line.type == 'gene']

    def get_features(self, gene_line):
        buffer_key = gene_line.attr['Name'] if 'Name' in gene_line.attr else\
            gene_line.attr['ID']
        if buffer_key in self.buffer:
            return self.buffer[buffer_key]

        lines = self.index.fetch(gene_line.chr, gene_line.start, gene_line.stop)
        genes = GffEntryIterator.get_features(GffLineIterator.parse_line(line) for line in lines)
        for gene in genes:
            if gene.name == gene_line.attr.get('Name', gene_line.attr['ID']):
                if len(self.buffer) > self.max_buffer:
                    self.buffer.popitem()
                self.buffer[buffer_key] = gene
                return gene
        raise KeyError('{}'.format(gene_line.attr['Name']))
