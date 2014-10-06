import os
import sys

from ebias.features import Resource, Target

from lhc.file_format.id_map import IdMap
from lhc.file_format.vcf_.iterator import VcfIterator as VcfIteratorParser
from lhc.file_format.vcf_.set_ import VcfSet as VcfSetParser

class VcfIterator(Target):
    
    EXT = ['.vcf', '.vcf.gz']
    TYPE = 'variant'
    PARSER = VcfIteratorParser
    TARGET = True
    OUT = ['variant', 'genomic_position']

    def calculate(self):
        return self.parser.next()

class VcfSet(Resource):
    """A set of variants parsed from a .vcf file
    """
    
    EXT = ['.vcf', '.vcf.gz']
    TYPE = 'variant'
    PARSER = VcfSetParser
    OUT = ['variant_set']
    
    def init(self, id_map=None, fr=None, to=None):
        if id_map is not None:
            id_map = IdMap(id_map, fr, to)
        fname = self.getFilename()
        if os.path.exists('%s.tbi'%fname):
            try:
                from lhc.file_format.vcf_.index import IndexedVcfFile
                self.parser = IndexedVcfFile(fname, id_map)
                return
            except ImportError:
                sys.stderr.write('Pysam not available. Parsing entire file.')
                pass
        self.parser = VcfSetParser(VcfIteratorParser(fname))
