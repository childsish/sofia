from bed_ import BedIterator, BedSet, IndexedBedFile

def iterEntries(fname):
    """ Convenience function """
    return BedIterator(fname)
