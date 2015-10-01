__author__ = 'Liam Childs'

from Bio.bgzf import BgzfReader
from lhc.indices.bgzf import load_index
from lhc.io.txt_ import EntityParser


class IndexedSet(object):
    def __init__(self, filename):
        self.fileobj = BgzfReader(filename)
        self.index = load_index(filename)

    def fetch(self, *args):
        res = []
        virtual_offsets = self.index.fetch(*args)
        for virtual_offset in virtual_offsets:
            self.fileobj.seek(virtual_offset)
            res.append(self.fileobj.readline())
        return res
