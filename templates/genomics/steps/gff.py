import gzip

from lhc.collections.inorder_access_interval_set import InOrderAccessIntervalSet
from lhc.interval import Interval
from lhc.io.gff.iterator import GffEntryIterator
from sofia.step import Step


class GffIterator(Step):

    IN = ['gff_file']
    OUT = ['genomic_feature']

    def __init__(self, gff_file):
        self.gff_file = gff_file.pop()
        self.iterator = None

    def run(self, genomic_feature):
        if self.iterator is None:
            fileobj = gzip.open(self.gff_file) if self.gff_file.endswith('.gz') else open(self.gff_file)
            self.iterator = GffEntryIterator(fileobj)
        try:
            iterator = self.iterator
            entry = iterator.next()
            while genomic_feature.push(entry):
                entry = iterator.next()
        except StopIteration:
            genomic_feature.push(StopIteration)

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

    def __init__(self, gff_file):
        self.gff_file = gff_file.pop()

    def run(self, genomic_feature_set):
        fileobj = gzip.open(self.gff_file) if self.gff_file.endswith('.gz') else open(self.gff_file)
        genomic_feature_set.push(InOrderAccessIntervalSet(GffEntryIterator(fileobj), key=gff_key))

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
