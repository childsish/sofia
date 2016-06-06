import gzip

from lhc.collections.inorder_access_interval_set import InOrderAccessIntervalSet
from lhc.interval import Interval
from lhc.io.gtf.iterator import GtfEntryIterator
from sofia.step import Step


class GtfIterator(Step):

    IN = ['gtf_file']
    OUT = ['genomic_feature']

    def __init__(self):
        self.fileobj = None

    def run(self, gtf_file):
        self.fileobj = gzip.open(gtf_file) if gtf_file.endswith('.gz') else open(gtf_file)
        for entry in GtfEntryIterator(self.fileobj):
            if entry.type == 'gene':
                entry.name = entry.name.rsplit('.')[0]
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


class GtfSet(Step):

    IN = ['gtf_file']
    OUT = ['genomic_feature_set']

    def __init__(self):
        self.fileobj = None

    def run(self, gtf_file):
        self.fileobj = gzip.open(gtf_file) if gtf_file.endswith('.gz') else open(gtf_file)
        yield InOrderAccessIntervalSet(GtfEntryIterator(self.fileobj),
                                       key=lambda line: Interval((line.chr, line.start), (line.chr, line.stop)))

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
