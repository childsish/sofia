from collections import namedtuple


class Iterator(object):
    def __init__(self, iterator, separator='\t', comment='#', has_header=False, formatter=None):
        self.line_number = 0

        self.iterator = iterator
        self.separator = separator
        self.comment = comment
        self.has_header = has_header

        self.header = []
        self.fields = None
        self.formatter = self._get_formatter(formatter)

    def __iter__(self):
        iterator = self.iterator
        separator = self.separator
        formatter = self.formatter
        line = iterator.next()
        while line != '':
            yield formatter(*line.strip('\r\n').split(separator))
            line = iterator.next()
            self.line_number += 1

    def _get_formatter(self, formatter=None):
        iterator = self.iterator
        comment = self.comment
        separator = self.separator

        line = iterator.next()
        self.line_number += 1
        while line.startswith(comment):
            self.header.append(line)
            line = iterator.next()
            self.line_number += 1

        if self.has_header:
            self.fields = line.strip().split(separator)
            line = iterator.next()
            self.line_number += 1
        else:
            self.fields = ['V{}'.format(i) for i, part in enumerate(line.strip('\r\n').split(separator))]

        if formatter is None:
            return namedtuple('Entry', self.fields)
        return formatter
