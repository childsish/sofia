from .entity import Entity, Column
from collections import namedtuple
from lhc.io.txt_.entity_parser import EntityParser


class Iterator(object):
    def __init__(self, iterator, entry_factory=None, comment='#', skip=0, delimiter='\t'):
        """
        Default assumes tab-delimited fields with no header and comments lines starting with "#"
        :param iterator: an iterable object
        :param entry_factory: an function that builds the entry from the line parts (after splitting)
        :param comment: the character used to denote the beginning of a comment
        :param skip: the number of lines to skip. Usually 0 or 1 (ie. no header or header)
        :param delimiter: the character used to split the line
        :return:
        """
        self.line_no = 0
        self.skipped = 0

        self.iterator = iterator
        self.entry_factory = self.guess_entity_factory(iterator) if entry_factory is None else entry_factory
        self.delimiter = delimiter
        self.skip = skip
        self.comment = comment

    def __iter__(self):
        return self

    def next(self):
        while True:
            line = self.iterator.next()
            self.line_no += 1
            if not line.startswith(self.comment):
                if self.skipped >= self.skip:
                    break
                self.skipped += 1

        parts = line.rstrip('\r\n').split(self.delimiter)
        return self.entry_factory(parts)

    @staticmethod
    def guess_entity_factory(iterable, comment='#', delimiter='\t', skip=0):
        skipped = 0
        hdrs = None
        entity_factory = None
        for line in iterable:
            if line.startswith(comment):
                hdrs = line[len(comment):]
            elif skipped >= skip:
                parts = line.rstrip('\r\n').split(delimiter)
                hdrs = ['V{}'.format(i + 1) for i in xrange(len(parts))] if hdrs is None else\
                    hdrs.rstrip('\r\n').split(delimiter)
                for i, hdr in enumerate(hdrs):
                    hdrs[i] = ''.join(c if c in EntityParser.VALID_CHARS else '_' for c in hdr)

                entity_factory = Entity(namedtuple('Entry', hdrs), [Column(str, i) for i in xrange(len(hdrs))])
                break
            else:
                hdrs = line
                skipped += 1
        if entity_factory is None:
            raise ValueError('unable to file')
        return entity_factory
