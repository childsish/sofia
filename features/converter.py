from ebias.features import Converter

class GeneIdConverter(Converter):
    
    IN = ['gene_id', 'gene_id_map']
    OUT = ['gene_id']
    
    def iterOutput(self, gene_id, gene_id_map):
        for outs in super(GeneIdConverter, self).iterOutput(gene_id, gene_id_map):
            yield outs
    
class ChromosomeIdConverter(Converter):
    
    IN = ['chromosome_id', 'chromosome_id_map']
    OUT = ['chromosome_id']
    
    def iterOutput(self, chromosome_id, chromosome_id_map):
        for outs in super(GeneIdConverter, self).iterOutput(chromosome_id, chromosome_id_map):
            yield outs
