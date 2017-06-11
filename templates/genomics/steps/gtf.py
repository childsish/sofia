import gzip

from sofia.step import Step
from lhc.io.gtf.iterator import GtfIterator as GtfEntryIterator, GtfLineIterator
try:
    from lhc.io.gtf.index import IndexedGtfFile as get_gtf_set
except ImportError:
    from lhc.collections.inorder_access_set import InOrderAccessSet

    def get_gtf_set(filename):
        fileobj = gzip.open(filename, 'rt') if filename.endswith('.gz') else open(filename, encoding='utf-8')
        return InOrderAccessSet(GtfEntryIterator(fileobj))


class GtfIterator(Step):

    IN = ['gtf_file']
    OUT = ['genomic_feature']

    def run(self, gtf_file):
        gtf_file = gtf_file[0]
        fileobj = gzip.open(gtf_file, 'rt') if gtf_file.endswith('.gz') else open(gtf_file, encoding='utf-8')
        for entry in GtfEntryIterator(GtfLineIterator(fileobj)):
            if entry.data['type'] == 'gene':
                entry.name = entry.data['name'].rsplit('.')[0]
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

    def run(self, gtf_file):
        for filename in gtf_file:
            yield get_gtf_set(filename)

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
