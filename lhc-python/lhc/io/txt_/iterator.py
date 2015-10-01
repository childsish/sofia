from .entity import Entity, Column
from collections import namedtuple
from lhc.io.txt_.entity_parser import EntityParser


class Iterator(object):
    def __init__(self, iterator, header='#', skip=0, delimiter='\t', entry_factory=None):
        """
        Default assumes tab-delimited fields with no header and comments lines starting with "#"
        :param iterator: an iterable object
        :param header: the character used to denote the beginning of a header (must occur before any data)
        :param skip: the number of lines to skip. Usually 0 or 1 (ie. no header or header)
        :param delimiter: the character used to split the line
        :param entry_factory: an function that builds the entry from the line parts (after splitting)
        :return:
        """
        self.header = []
        self.line_number = 0

        line = iterator.next()
        self.line_number += 1
        while line.startswith(header):
            self.header.append(line)
            line = iterator.next()
            self.line_number += 1
        for i in xrange(skip):
            line = iterator.next()
            self.line_number += 1
        self.line = line

        self.iterator = iterator
        self.delimiter = delimiter
        self.entry_factory = self.guess_entity_factory(line) if entry_factory is None else entry_factory

    def __iter__(self):
        return self

    def next(self):
        try:
            line = self.iterator.next()
            self.line_number += 1
        except StopIteration, e:
            if self.line is None:
                raise e
            line = None
        entry = self.entry_factory(self.line.rstrip('\r\n').split(self.delimiter))
        self.line = line
        return entry

    def guess_entity_factory(self, line):
        parts = line.rstrip('\r\n').split(self.delimiter)
        hdrs = ['V{}'.format(i + 1) for i in xrange(len(parts))] if len(self.header) == 0 else\
            self.header[-1].rstrip('\r\n').split(self.delimiter)
        for i, hdr in enumerate(hdrs):
            hdrs[i] = ''.join(c if c in EntityParser.VALID_CHARS else '_' for c in hdr)
        return Entity(namedtuple('Entry', hdrs), [Column(str, i) for i in xrange(len(hdrs))])
