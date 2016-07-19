import gzip

from lhc.collections.inorder_access_set import InOrderAccessSet
from lhc.io.vcf.iterator import VcfEntryIterator
from lhc.filetools import SharedFile
from sofia.step import Step


class IterateVcf(Step):

    IN = ['vcf_file']
    OUT = ['variant']

    def __init__(self, vcf_file):
        self.vcf_file = vcf_file.pop()
        self.fileobj = None
        self.iterator = None

    def run(self, variant):
        if self.iterator is None:
            self.fileobj = gzip.open(self.vcf_file) if self.vcf_file.endswith('.gz') else SharedFile(self.vcf_file)
            self.iterator = VcfEntryIterator(self.fileobj)
        try:
            iterator = self.iterator
            entry = iterator.next()
            while variant.push(entry):
                entry = iterator.next()
        except StopIteration:
            variant.push(StopIteration)

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


class GetVcfSet(Step):

    IN = ['vcf_file']
    OUT = ['variant_set']

    def __init__(self, vcf_file):
        self.vcf_file = vcf_file.pop()
    
    def run(self, variant_set):
        fileobj = gzip.open(self.vcf_file) if self.vcf_file.endswith('.gz') else SharedFile(self.vcf_file)
        variant_set.push(InOrderAccessSet(VcfEntryIterator(fileobj)))
        variant_set.push(StopIteration)

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
