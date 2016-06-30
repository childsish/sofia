import gzip

from lhc.collections.inorder_access_interval_set import InOrderAccessIntervalSet
from lhc.interval import Interval
from lhc.io.gff.iterator import GffEntryIterator
from sofia.step import Step


class GffIterator(Step):

    IN = ['gff_file']
    OUT = ['genomic_feature']

    def run(self, gff_file):
        gff_file = gff_file[0]
        fileobj = gzip.open(gff_file) if gff_file.endswith('.gz') else open(gff_file)
        for entry in GffEntryIterator(fileobj):
            yield entry

    @classmethod
    def get_out_resolvers(cls):
        return {
            'filename': cls.resolve_out_filename
        }

    @classmethod
    def resolve_out_filename(cls, ins):
        return {
            'genomic_feature': set()
        }


class GffSet(Step):

    IN = ['gff_file']
    OUT = ['genomic_feature_set']

    def run(self, gff_file):
        gff_file = gff_file[0]
        fileobj = gzip.open(gff_file) if gff_file.endswith('.gz') else open(gff_file)
        yield InOrderAccessIntervalSet(GffEntryIterator(fileobj), key=gff_key)

    @classmethod
    def get_out_resolvers(cls):
        return {
            'filename': cls.resolve_out_filename
        }

    @classmethod
    def resolve_out_filename(cls, ins):
        return {
            'genomic_feature_set': set()
        }


def gff_key(line):
    return Interval((line.chr, line.start), (line.chr, line.stop))
