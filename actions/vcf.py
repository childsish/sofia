from sofia_.action import Resource, Target
from modules.file_formats.vcf_.iterator import VcfIterator as VcfIteratorParser
from modules.file_formats.vcf_.set_ import VcfSet as VcfSetParser
try:
    from modules.file_formats.vcf_.index import IndexedVcfFile
except ImportError:
    import sys
    sys.stderr.write('Pysam not available. Vcf file access will be slower.')
    IndexedVcfFile = lambda fname: VcfSetParser(VcfIteratorParser(fname))


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
    
    def init(self):
        self.parser = IndexedVcfFile(self.getFilename())
