__author__ = 'Liam Childs'

from collections import namedtuple

Line = namedtuple('Line', ('type', 'value'))


class Iterator(object):
    def __init__(self, iterator, comment='#', has_header=False):
        """ Classify string in an iterator into comment, header or line

        :param iterator: iterator over string (ie. file object)
        :param comment: leading characters indicating a comment
        :param has_header: one line with column names?
        :return:
        """
        self.line_number = 0
        self.has_read_header = False

        self.iterator = iterator
        self.comment = comment
        self.has_header = has_header

    def __iter__(self):
        for line in self.iterator:
            if line.startswith(self.comment):
                yield Line(type='comment', value=line)
            elif self.has_header and not self.has_read_header:
                self.has_read_header = True
                yield Line(type='header', value=line)
            else:
                yield Line(type='line', value=line)
            self.line_number += 1
