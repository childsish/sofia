from sofia_.features import Feature


class GetGeneModelByGeneId(Feature):

    IN = ['gene_model_set', 'gene_id']
    OUT = ['gene_model']

    def calculate(self, gene_model_set, gene_id):
        gene = gene_model_set.getGeneByGeneId(gene_id)
        return {'gene_id': gene_id, 'chromosome_id': gene.ivl.chr, 'gene_model': gene}


class GetGeneModelByPosition(Feature):
    
    IN = ['gene_model_set', 'genomic_position']
    OUT = ['gene_model']

    def calculate(self, gene_model_set, genomic_position):
        #TODO: select correct gene
        gene_model = gene_model_set.getGenesAtPosition(
            genomic_position['chromosome_id'],
            genomic_position['chromosome_pos'])
        if gene_model is None or len(gene_model) == 0:
            return None
        gene = gene_model[0]
        return {'gene_id': gene.name, 'chromosome_id': gene.ivl.chr, 'gene_model': gene}


class GetGeneModelByInterval(Feature):
        
    IN = ['gene_model_set', 'genomic_interval']
    OUT = ['gene_model']

    def calculate(self, gene_model_set, genomic_interval):
        #TODO: select correct gene
        gene_model = gene_model_set.getGenesInInterval(
            genomic_interval['chromosome_id'],
            genomic_interval['start'],
            genomic_interval['stop'])
        if gene_model is None or len(gene_model) == 0:
            return None
        gene = gene_model[0]
        return {'gene_id': gene.name, 'chromosome_id': gene.ivl.chr, 'gene_model': gene}
