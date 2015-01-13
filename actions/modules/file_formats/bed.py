from bed_.iterator import BedIterator
from bed_.set_ import BedSet
from bed_.index import IndexedBedFile


def iter_entries(fname):
    """ Convenience function """
    return BedIterator(fname)
