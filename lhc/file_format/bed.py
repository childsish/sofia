from bed_.iterator import BedEntryIterator


def iter_bed(fname):
    it = BedEntryIterator(fname)
    for entry in it:
        yield entry
    it.close()
