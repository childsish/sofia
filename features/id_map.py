from ebias.features import Feature, Resource
from ebias.entity import Entity

from lhc.file_format.id_map import IdMap as IdMapParser

class IdMap(Resource):
    
    OUT = ['id_map']
    EXT = ['.txt', '.txt.gz']
    TYPE = 'id'

    def init(self, id_map=None, fr=None, to=None):
        fname = self.getFilename()
        id_map = id_map if id_map is None else\
            IdMapParser(id_map, fr, to)
        self.parser = IdMapParser(fname, id_map=id_map)
    
    @classmethod
    def iterOutput(cls, resource):
        fhndl = open(resource.fname)
        hdrs = fhndl.next().strip().split('\t')
        fhndl.close()
        yield { 
            cls.OUT[0]: Entity({'hdrs': hdrs})
        }

class GeneIdMap(IdMap):
    
    OUT = ['gene_id_map']
    EXT = ['.txt', '.txt.gz']
    TYPE = 'gene_id'

class ChromosomeIdMap(IdMap):

    OUT = ['chromosome_id_map']
    EXT = ['.txt', '.txt.gz']
    TYPE = 'chromosome_id'

class GetPathwayIdByGeneId(Feature):
    
    IN = ['gene_id', 'pathway_id_map']
    OUT = ['pathway_id']
    
    def calculate(self, gene_id, id_map):
        try:
            return id_map[gene_id]
        except KeyError:
            pass
        return None
    
    def format(self, pathway_id):
        if isinstance(pathway_id, basestring):
            return pathway_id
        return ','.join(pathway_id)

class GetAnnotationByGeneId(Feature):

    IN = ['gene_id', 'annotation_map']
    OUT = ['annotation']

    def calculate(self, gene_id, id_map):
        try:
            return id_map[gene_id]
        except KeyError:
            pass
        return None
    
    def format(self, annotation):
        if isinstance(annotation, basestring):
            return annotation
        return ','.join(annotation)
