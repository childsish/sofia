import string

from collections import namedtuple
from entry_builder import EntryBuilder


class BuilderGuesser(object):

    VALID_CHARS = set(string.ascii_letters + string.digits + '_')

    def guess_type(self, fname, comment='#', delimiter='\t', skip=0):
        fhndl = open(fname)
        skipped = 0
        hdrs = None
        builder = None
        for line in fhndl:
            if line.startswith(comment):
                hdrs = line[len(comment):]
                continue
            elif skipped >= skip:
                parts = line.rstrip('\r\n').split(delimiter)
                hdrs = ['V{}'.format(i + 1) for i in xrange(len(parts))] if hdrs is None else\
                    hdrs.rstrip('\r\n').split(delimiter)
                for i, hdr in enumerate(hdrs):
                    hdrs[i] = ''.join(c if c in self.VALID_CHARS else '_' for c in hdr)

                builder = EntryBuilder(namedtuple('Entry', hdrs), columns=range(len(hdrs)))
                break
            else:
                hdrs = line
                skipped += 1
        fhndl.close()
        if builder is None:
            raise ValueError('Unable to parse {}'.format(fname))
        return builder
