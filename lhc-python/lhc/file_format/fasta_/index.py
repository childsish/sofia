import os
try:
    from pysam import Fastafile
except ImportError:
    import sys
    from iterator import FastaEntryIterator
    from set_ import FastaSet
    sys.stderr.write('Could not find pysam. Reading entire file instead.\n')
    Fastafile = lambda fname: FastaSet(FastaEntryIterator(fname))


class IndexedFastaFile(object):
    def __init__(self, fname):
        self.fname = os.path.abspath(fname)
        iname1 = '{}.fai'.format(self.fname)
        #iname2 = '%s.bzi' % self.fname
        if not (os.path.exists(iname1) and os.path.exists(iname1)):
            raise ValueError('File missing fasta index. Try: samtools faidx <FILENAME>.')
        self.index = pysam.Fastafile(fname)

    def __getitem__(self, key):
        if isinstance(key, basestring):
            return IndexedFastaEntry(key, self.index)
        elif hasattr(key, 'chr') and hasattr(key, 'pos'):
            return self.index.fetch(key.chr, key.pos, key.pos + 1)
        elif hasattr(key, 'chr') and hasattr(key, 'start') and hasattr(key, 'stop'):
            return self.get_interval(key.chr, key.start, key.stop)
        raise NotImplementedError('Random access not implemented for {}'.format(type(key)))

    def get_interval(self, chr, start, stop):
        return self.index.fetch(chr, start, stop)


class IndexedFastaEntry(object):
    def __init__(self, chr, index):
        self.chr = chr
        self.index = index

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.index.fetch(self.chr, key, key + 1)
        elif hasattr(key, 'start') and hasattr(key, 'stop'):
            return self.index.fetch(self.chr, key.start, key.stop)
        raise NotImplementedError('Random access not implemented for {}'.format(type(key)))
