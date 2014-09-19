import os
import sys

from ebias.resource import Resource, Target

from lhc.file_format.gtf_.iterator import GtfIterator as GtfIteratorParser
from lhc.file_format.gtf_.set_ import GtfSet as GtfSetParser

class GtfIterator(Target):
    
    EXT = ['.gtf', '.gtf.gz']
    TYPE = 'gene_model'
    PARSER = GtfIteratorParser
    TARGET = True
    OUT = ['gene_model_iterator']

class GtfSet(Resource):
    
    EXT = ['.gtf', '.gtf.gz']
    TYPE = 'gene_model'
    PARSER = GtfSetParser
    OUT = ['gene_model_set']

    def init(self, **kwargs):
        fname = self.getFilename()
        if fname.endswith('.gz'):
            from lhc.file_format.gtf_.index import IndexedGtfFile
        self.parser = IndexedGtfFile(fname) if os.path.exists('%s.tbi'%fname)\
            else GtfSetParser(GtfIteratorParser(fname))
