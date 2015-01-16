from bed_.iterator import BedEntryIterator
from bed_.set_ import BedSet
from bed_.index import IndexedBedFile


def iter_entries(fname):
    """ Convenience function """
    return BedEntryIterator(fname)
