from ebias.feature import Feature

class GetGeneModelByHeader(Feature):
    
    IN = ['gene_model_set', 'header']
    OUT = ['gene_model']
    
    def calculate(self, gene_model_set, header):
        return gene_model_set[header]

class GetGeneModelByPosition(Feature):
    
    IN = ['gene_model_set', 'genomic_position']
    OUT = ['gene_model']

    def calculate(self, gene_model_set, genomic_position):
        res = gene_model_set[genomic_position]
        if res is None or len(res) == 0:
            return None 
        return res[0]
