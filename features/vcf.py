import os
import sys

from sofia.features import Resource, Target

from lhc.file_format.id_map import IdMap
from lhc.file_format.vcf_.iterator import VcfIterator as VcfIteratorParser
from lhc.file_format.vcf_.set_ import VcfSet as VcfSetParser

class VcfIterator(Target):
    
    EXT = ['.vcf', '.vcf.gz']
    OUT = ['variant']
    
    def init(self):
        self.parser = VcfIteratorParser(self.getFilename())

    def calculate(self):
        variant = self.parser.next()
        genomic_position = {'chromosome_id': variant.chr,
            'chromosome_pos': variant.pos}
        return {'genomic_position': genomic_position, 'variant': variant}

class VcfSet(Resource):
    """A set of variants parsed from a .vcf file
    """
    
    EXT = ['.vcf', '.vcf.gz']
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
