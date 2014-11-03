from ebias.features import Feature, Resource
from ebias.entity import Entity

from lhc.file_format.id_map import IdMap as IdMapParser

class IdMap(Resource):
    
    OUT = ['id_map']
    EXT = ['.txt', '.txt.gz']

    def init(self, id_map=None, fr=None, to=None):
        fname = self.getFilename()
        id_map = id_map if id_map is None else\
            IdMapParser(id_map, fr, to)
        self.parser = IdMapParser(fname)
    
    @classmethod
    def getOutput(cls, ins={}, outs={}, attr={}):
        fhndl = open(ins['resource'].fname)
        hdrs = fhndl.next().strip().split('\t')
        fhndl.close()
        return { 
            cls.OUT[0]: Entity(cls.OUT[0], {'hdrs': hdrs})
        }

class GeneIdMap(IdMap):
    
    OUT = ['gene_id_map']
    EXT = ['.txt', '.txt.gz']

class ChromosomeIdMap(IdMap):

    OUT = ['chromosome_id_map']
    EXT = ['.txt', '.txt.gz']
