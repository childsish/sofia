from gff_.iterator import GffEntryIterator


def iter_gff(fname):
    return GffEntryIterator(fname)
