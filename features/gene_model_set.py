from ebias.feature import Feature

class IterateGeneModel(Feature):
    
    IN = ['gene_model_iterator']
    OUT = ['gene_model']
    
    def calculate(self, gene_model_iterator):
        return gene_model_iterator.next()

class GetGeneModelByHeader(Feature):
    
    IN = ['gene_model_set', 'header']
    OUT = ['gene_model']
    
    def calculate(self, gene_model_set, header):
        return {header: gene_model_set[header]}

class GetGeneModelByPosition(Feature):
    
    IN = ['gene_model_set', 'genomic_position']
    OUT = ['gene_model']

    def calculate(self, gene_model_set, genomic_position):
        gene_models = gene_model_set[genomic_position]
        return {model.name: model for model in gene_models}

