from modules.resource import Resource

class AccessFastaByModel(Resource):
    
    EXT = 'fasta'
    IN = ['fasta', 'model']
    OUT = ['nucleotide_sequence']

    def calculate(self, model):
        return model.getSubSeq(self.data)

class AccessFastaByHeader(Resource):
    
    EXT = 'fasta'
    IN = ['fasta', 'header']

    def calculate(self, string):
        return self.data[string]
