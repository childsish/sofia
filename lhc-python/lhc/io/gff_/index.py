from iterator import GffEntryIterator, GffLineIterator


class IndexedGffFile(object):
    def __init__(self, index):
        self.index = index

    def fetch(self, chr, start, stop):
        lines = [GffLineIterator.parse_line(line) for line in self.index.fetch(chr, start, stop)]
        return [self.get_features(line) for line in lines if line.type == 'gene']

    def get_features(self, gene_line):
        genes = GffEntryIterator.get_features(self.index.fetch(gene_line.chr, gene_line.start, gene_line.stop))
        for gene in genes:
            if gene.name == gene_line.attr['ID']:
                return gene
        raise KeyError('{}'.format(gene_line.attr['ID']))
