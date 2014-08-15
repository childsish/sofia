from ebias.resource import Resource

from lhc.file_format.gtf_.iterator import GtfIterator as GtfIteratorParser
from lhc.file_format.gtf_.set_ import GtfSet as GtfSetParser
from lhc.file_format.gtf_.index import IndexedGtfFile

class GtfIterator(Resource):
    
    EXT = ['.gtf', '.gtf.gz']
    TYPE = 'gene_model'
    PARSER = GtfIteratorParser
    TARGET = True
    OUT = ['gene_model_iterator']

class GtfSet(Resource):
    
    EXT = ['.gtf', '.gtf.gz', '.gtf.idx']
    TYPE = 'gene_model'
    PARSER = GtfSetParser
    OUT = ['gene_model_set']

    def init(self, **kwargs):
        fname = self.getFilename()
        self.parser = IndexedGtfFile(fname) if fname.endswith('.gtf.idx') else\
            GtfSetParser(GtfIteratorParser(fname))

