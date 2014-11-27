import sys
import os

from sofia_.features import Resource, Target

from lhc.file_format.gtf_.iterator import GtfIterator as GtfIteratorParser
from lhc.file_format.gtf_.set_ import GtfSet as GtfSetParser

class GtfIterator(Target):
    
    EXT = ['.gtf', '.gtf.gz']
    TYPE = 'gene_model'
    OUT = ['gene_model_iterator']

    def init(self):
        self.parser = GtfIteratorParser(self.getFilename())

class GtfSet(Resource):
    
    EXT = ['.gtf', '.gtf.gz']
    TYPE = 'gene_model'
    OUT = ['gene_model_set']

    def init(self):
        fname = self.getFilename()
        if os.path.exists('%s.tbi'%fname):
            try:
                from lhc.file_format.gtf_.index import IndexedGtfFile
                self.parser = IndexedGtfFile(fname)
                return
            except ImportError:
                sys.stderr.write('Pysam not available. Parsing entire file.')
                pass
        self.parser = GtfSetParser(GtfIteratorParser(fname))
