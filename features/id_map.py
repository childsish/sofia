from ebias.features import Feature, Resource

from lhc.file_format.id_map import IdMap as IdMapParser

class IdMap(Resource):
    
    OUT = ['id_map']
    EXT = ['.txt', '.txt.gz']

    def init(self, fr=None, to=None):
        fname = self.getFilename()
        self.parser = IdMapParser(fname, fr, to)

class GetPathwayIdByGeneId(Feature):
    
    IN = ['gene_id', 'id_map']
    OUT = ['pathway_id']
    
    def calculate(self, gene_id, id_map):
        return id_map[gene_id]
