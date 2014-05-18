from modules.feature import Feature

class GetGenePosition(Feature):
    
    IN = ['genomic_position', 'model']
    OUT = ['gene_position']

    def calculate(self, genomic_position, model):
        return model.getRelPos(genomic_position)
