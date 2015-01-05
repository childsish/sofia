import os
import pysam

from iterator import VcfEntryIterator


class IndexedVcfFile(object):
    def __init__(self, fname):
        """ Initialise an indexed vcf file.
        
        :param fname: the name of the indexed vcf file.
            Must end in .vcf or .vcf.gz
        """
        self.fname = os.path.abspath(fname)
        iname = '{}.tbi'.format(self.fname)
        if not os.path.exists(iname):
            raise ValueError('File missing interval index. Try: tabix -p vcf <FILENAME>.')
        self.index = pysam.Tabixfile(self.fname)
        self.iterator = VcfEntryIterator(self.fname)

    def __getitem__(self, key):
        if not hasattr(key, 'chr'):
            raise NotImplementedError('Random access not implemented for {}'.format(type(key)))
        # TODO: assumes a single mapping
        start = key.start if hasattr(key, 'start') else \
            key.pos if hasattr(key, 'pos') else \
            None
        if start is None:
            raise NotImplementedError('Random access not implemented for {}'.format(type(key)))
        stop = key.stop if hasattr(key, 'stop') else \
            start + len(key.ref) if hasattr(key, 'ref') else \
            start + 1
        lines = self.index.fetch(key.chr, start, stop)
        return [self.iterator._parse_line(line) for line in lines]

    def get_variants_at_position(self, chr, pos):
        lines = self.index.fetch(chr, pos, pos + 1)
        return [self.iterator._parse_line(line) for line in lines]

    def get_variants_in_interval(self, chr, start, stop):
        lines = self.index.fetch(chr, start, stop)
        return [self.iterator._parse_line(line) for line in lines]
