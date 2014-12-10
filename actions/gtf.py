import sys
import os

from sofia_.action import Resource, Target

from modules.file_formats.gtf import GtfIterator as GtfIteratorParser, GtfSet as GtfSetParser


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
