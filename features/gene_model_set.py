from ebias.feature import Feature

class GetGeneModelByPosition(Feature):
    
    IN = ['gene_model_set', 'genomic_position']
    OUT = ['gene_model']

    def calculate(self, gene_model_set, genomic_position):
        gene_model = gene_model_set[genomic_position]
        if gene_model is None or len(gene_model) == 0:
            return None 
        return gene_model[0]

class GetGeneModelByInterval(Feature):
        
    IN = ['gene_model_set', 'genomic_interval']
    OUT = ['gene_model']

    def calculate(self, gene_model_set, genomic_interval):
        gene_model = gene_model_set[genomic_interval]
        if gene_model is None or len(gene_model) == 0:
            return None
        return gene_model[0]
