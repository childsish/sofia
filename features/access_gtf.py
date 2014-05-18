from modules.resource import Resource

class AccessGtfByPosition(Resource):
    
    EXT = 'gtf'
    IN = ['gtf', 'genomic_position']
    OUT = ['model']

    def calculate(self, genomic_position):
        return self.data[genomic_position]
