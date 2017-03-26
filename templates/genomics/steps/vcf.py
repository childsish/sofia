from __future__ import with_statement

import gzip

from lhc.collections.inorder_access_set import InOrderAccessSet
from lhc.io.vcf.iterator import VcfIterator as VcfEntryIterator
from sofia.step import Step


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
        vcf_file = vcf_file[0]
        self.fileobj = gzip.open(vcf_file, 'rt') if vcf_file.endswith('.gz') else open(vcf_file, encoding='utf-8')
        yield InOrderAccessSet(VcfEntryIterator(self.fileobj))

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
