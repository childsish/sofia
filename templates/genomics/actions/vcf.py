from sofia_.action import Resource, Target
from lhc.io.vcf_.iterator import VcfEntryIterator, VcfLineIterator as VcfIteratorParser
from lhc.io.vcf_.set_ import VcfSet as VcfSetParser


class VcfIterator(Target):
    
    EXT = ['.vcf', '.vcf.gz']
    OUT = ['variant']
    
    def init(self):
        self.parser = iter(VcfEntryIterator(self.get_filename()))

    def calculate(self):
        variant = self.parser.next()
        return {
            'genomic_position': {
                'chromosome_id': variant.chr,
                'chromosome_pos': variant.pos
            },
            'ref': variant.ref,
            'alt': variant.alt,
            'qual': variant.qual,
            'info': variant.info,
            'samples': variant.samples
        }


class VcfSet(Resource):
    """A set of variants parsed from a .vcf file
    """
    
    EXT = ['.vcf', '.vcf.gz']
    OUT = ['variant_set']
    
    def init(self):
        try:
            from lhc.io.vcf_.index import IndexedVcfFile
        except ImportError:
            import sys
            sys.stderr.write('Pysam not available. Vcf file access will be slower.\n')
            IndexedVcfFile = lambda fname: VcfSetParser(VcfIteratorParser(fname))
        self.parser = IndexedVcfFile(self.get_filename())