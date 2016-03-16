from collections import namedtuple


class FastaEntry(namedtuple('FastaEntry', ('hdr', 'seq'))):
    def __str__(self):
        """
        Represent the entry as a string. Only intended for entries with short sequences.

        :return: The fasta entry as a string
        """
        return '{}\n{}\n'.format(self.hdr, self.seq)


class FastaEntryIterator(object):
    def __init__(self, iterator, hdr_parser=None):
        self.iterator = iterator
        self.hdr_parser = (lambda x: x) if hdr_parser is None else hdr_parser
        self.line = self.iterator.next()
    
    def __iter__(self):
        return self

    def next(self):
        if self.line is None:
            raise StopIteration()

        seq = []
        for line in self.iterator:
            if line.startswith('>'):
                hdr = self.hdr_parser(self.line[1:].strip())
                self.line = line
                return FastaEntry(hdr, ''.join(seq))
            seq.append(line.strip())
        hdr = self.hdr_parser(self.line[1:].strip())
        self.line = None
        return FastaEntry(hdr, ''.join(seq))

    def close(self):
        if hasattr(self.iterator, 'close'):
            self.iterator.close()

    def __del__(self):
        self.close()
