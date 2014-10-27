from ebias.features import Converter

class GeneIdConverter(Converter):
    
    IN = ['gene_id', 'gene_id_map']
    OUT = ['gene_id']
    
class ChromosomeIdConverter(Converter):
    
    IN = ['chromosome_id', 'chromosome_id_map']
    OUT = ['chromosome_id']
