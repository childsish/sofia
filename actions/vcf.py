from sofia_.action import Resource, Target
from lhc.file_format.vcf_.iterator import VcfEntryIterator as VcfIteratorParser
from lhc.file_format.vcf_.set_ import VcfSet as VcfSetParser
try:
    from lhc.file_format.vcf_.index import IndexedVcfFile
except ImportError:
    import sys
    sys.stderr.write('Pysam not available. Vcf file access will be slower.\n')
    IndexedVcfFile = lambda fname: VcfSetParser(VcfIteratorParser(fname))


class VcfIterator(Target):
    
    EXT = ['.vcf', '.vcf.gz']
    OUT = ['variant']
    
    def init(self):
        self.parser = iter(VcfIteratorParser(self.get_filename()))

    def calculate(self):
        variant = self.parser.next()
        return {
            'variant': variant,
            'genomic_position': {
                'chromosome_id': variant.chr,
                'chromosome_pos': variant.pos
            },
            'reference_allele': variant.ref,
            'alternate_allele': variant.alt,
            'variant_quality': variant.qual
        }


class VcfSet(Resource):
    """A set of variants parsed from a .vcf file
    """
    
    EXT = ['.vcf', '.vcf.gz']
    OUT = ['variant_set']
    
    def init(self):
        self.parser = IndexedVcfFile(self.get_filename())
