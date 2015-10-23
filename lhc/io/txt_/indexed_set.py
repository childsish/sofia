__author__ = 'Liam Childs'

from Bio.bgzf import BgzfReader
from lhc.indices.tracked_index import load_index
from lhc.io.txt_ import EntityParser
from lhc.collections.tracked_set import multivariate_overlap


class IndexedSet(object):
    def __init__(self, filename, format='s1'):
        self.fileobj = BgzfReader(filename)
        self.index = load_index(filename + '.lci')
        self.entity_parser = EntityParser().parse(format)

    def fetch(self, *args):
        virtual_offsets = self.index.fetch(*args)
        for fr, to in virtual_offsets:
            self.fileobj.seek(fr)
            while self.fileobj.tell() <= to:
                entity = self.entity_parser(self.fileobj.readline())
                if multivariate_overlap(entity, args):
                    yield entity
