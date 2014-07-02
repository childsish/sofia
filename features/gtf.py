from ebias.feature import Feature

class AccessGtfByPosition(Feature):
    
    IN = ['gtf', 'genomic_position']
    OUT = ['gene_model']

    def calculate(self, gtf, genomic_position):
        res = gtf[genomic_position]
        if res is None or len(res) == 0:
            return None 
        return res[0]
