__author__ = 'Liam Childs'

import gzip

from collections import OrderedDict
from operator import or_
from struct import pack, unpack


class TabixIndex(object):
    def __init__(self, filename):
        fhndl = gzip.open(filename, 'rb')
        magic, n_ref, self.format, self.col_seq, self.col_beg, self.col_end, self.meta, self.skip, l_nm =\
            unpack('<4siiiiiiii', fhndl.read(36))
        names = unpack('<{}s'.format(l_nm), fhndl.read(l_nm))[0].strip('\x00').split('\x00')
        self.bins = OrderedDict()
        self.ioffs = OrderedDict()
        for name in names:
            n_bins = unpack('<i', fhndl.read(4))[0]
            self.bins[name] = OrderedDict()
            for bin in xrange(n_bins):
                bin, n_chunk = unpack('<Ii', fhndl.read(8))
                chunks = [unpack('<QQ', fhndl.read(16)) for chunk in xrange(n_chunk)]
                self.bins[name][bin] = set(chunks)
            n_intv = unpack('<i', fhndl.read(4))[0]
            self.ioffs[name] = unpack('<' + n_intv * 'Q', fhndl.read(8 * n_intv))

    def fetch(self, chromosome, start, stop):
        bins = self.get_overlapping_bins(start, stop)
        chunks = reduce(or_, (self.bins[chromosome][bin] for bin in bins))
        print chunks

    def get_bin(self, start, stop):
        stop -= 1
        for rshift, lshift in [(14, 15), (17, 12), (20, 9), (23, 6), (26, 3)]:
            if start >> rshift == stop >> rshift:
                return ((1 << lshift) - 1) / 7 + (start >> rshift)
        return 0

    def get_overlapping_bins(self, start, stop):
        stop -= 1
        res = [0]
        for c, rshift in [(1, 26), (9, 23), (73, 20), (585, 17), (4681, 14)]:
            res.extend(xrange(c + (start >> rshift), c + (stop >> rshift)))
        return res

    def write_to_file(self, filename):
        concatenated_names = '\x00'.join(self.bins) + '\x00'

        fileobj = gzip.open(filename, 'wb')
        fileobj.write(pack('>4siiiiiiii{}s'.format(len(concatenated_names)), 'TBI\x00', len(self.bins), self.format,
                           self.col_seq, self.col_beg, self.col_end, self.meta, self.skip, len(concatenated_names),
                           concatenated_names))
        for name in self.bins:
            fileobj.write(pack('<i', len(self.bins[name])))
            for bin in self.bins:
                fileobj.write(pack('<Ii', bin, len(self.bins[name][bin])))
                for cnk_beg, cnk_end in self.bins[name][bin]:
                    fileobj.write(pack('<QQ', cnk_beg, cnk_end))
            fileobj.write(pack('<i', len(self.ioffs[name])))
        fileobj.close()
