from __future__ import with_statement

import gzip

from lhc.collections.inorder_access_set import InOrderAccessSet
from lhc.io.vcf.iterator import VcfEntryIterator
from sofia.step import Step


class VcfIterator(Step):

    IN = ['vcf_file']
    OUT = ['variant']

    def run(self, vcf_file):
        with gzip.open(vcf_file) if vcf_file.endswith('.gz') else open(vcf_file) as fileobj:
            for entry in VcfEntryIterator(fileobj):
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
    
    def run(self, vcf_file):
        with gzip.open(vcf_file) if vcf_file.endswith('.gz') else open(vcf_file) as fileobj:
            yield InOrderAccessSet(VcfEntryIterator(fileobj))

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
