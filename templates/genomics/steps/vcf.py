import gzip

from sofia.step import Step
from lhc.io.vcf.iterator import VcfIterator as VcfEntryIterator
try:
    from lhc.io.vcf.index import IndexedVcfFile as get_vcf_set
except ImportError:
    from lhc.collections.inorder_access_set import InOrderAccessSet

    def get_vcf_set(filename):
        fileobj = gzip.open(filename, 'rt') if filename.endswith('.gz') else open(filename, encoding='utf-8')
        return InOrderAccessSet(VcfEntryIterator(fileobj))


class VcfIterator(Step):

    IN = ['vcf_file']
    OUT = ['variant']

    def __init__(self):
        self.fileobj = None

    def run(self, vcf_file):
        vcf_file = vcf_file[0]
        self.fileobj = gzip.open(vcf_file, 'rt') if vcf_file.endswith('.gz') else open(vcf_file, encoding='utf-8')
        for entry in VcfEntryIterator(self.fileobj):
            yield entry

    @classmethod
    def get_out_resolvers(cls):
        return {
            'filename': cls.resolve_out_filename
        }

    @classmethod
    def resolve_out_filename(cls, ins):
        return {
            'variant': set()
        }


class VcfSet(Step):

    IN = ['vcf_file']
    OUT = ['variant_set']

    def __init__(self):
        self.fileobj = None
    
    def run(self, vcf_file):
        for filename in vcf_file:
            yield get_vcf_set(filename)

    @classmethod
    def get_out_resolvers(cls):
        return {
            'filename': cls.resolve_out_filename
        }

    @classmethod
    def resolve_out_filename(cls, ins):
        return {
            'variant_set': set()
        }
