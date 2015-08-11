__author__ = 'Liam Childs'

from .tokeniser import GenbankTokeniser
from collections import namedtuple
from itertools import izip, tee
from lhc.binf.genomic_coordinate import NestedGenomicInterval, GenomicInterval

HeaderStep = namedtuple('HeaderStep', ('header', 'indent'))


class GbkIterator(object):
    def __init__(self, fileobj):
        self.line_no = 0
        self.tokeniser = GenbankTokeniser()
        fileobj = iter(fileobj)
        self.hdr = self._parse_headers(fileobj)
        a, b = tee(fileobj)
        next(b, None)
        self.it = izip(a, b)

    def __iter__(self):
        return self

    def next(self):
        key = None
        value = []
        for c, n in self.it:
            self.line_no += 1
            if key is None:
                key = c[:21].strip()
            if key == 'ORIGIN':
                raise StopIteration()
            value.append(c[21:].strip())
            if n[:21].strip() != '' or n[21] == '/':
                break
        interval = self._parse_nested_interval(self.tokeniser.tokenise(''.join(value)))
        interval.type = key
        interval.data = dict(self._iter_qualifiers(self.it))
        return interval

    def _parse_headers(self, iterator):
        headers = {}
        header_path = []
        c_value = []
        for line in iterator:
            self.line_no += 1
            header = line[:12].strip()
            indent = len(line[:12]) - len(line[:12].lstrip(' '))
            value = line[12:].strip()
            if header == 'FEATURES':
                break
            elif header == '':
                c_value.append(value)
                continue
            else:
                nested_header = headers
                for step_header, step_index in header_path:
                    if step_header == 'REFERENCE':
                        nested_header = nested_header[step_header][-1]
                    else:
                        if step_header not in nested_header:
                            nested_header[step_header] = {}
                        nested_header = nested_header[step_header]
                nested_header['value'] = ' '.join(c_value)
                c_value = [value]

                if header == 'REFERENCE':
                    if header not in headers:
                        headers[header] = []
                    headers[header].append({})

            while len(header_path) > 0 and indent < header_path[-1].indent:
                header_path.pop()
            if len(header_path) == 0 or indent > header_path[-1].indent:
                header_path.append(HeaderStep(header, indent))
            else:  # indent == header_path[-1].indent
                header_path[-1] = HeaderStep(header, indent)
        return headers

    @classmethod
    def _parse_nested_interval(cls, tokens):
        """ Parses a super range.
         SuperRange ::= Range | Join | Complement
        """
        if tokens[0].isdigit():
            return cls._parse_interval(tokens)
        elif tokens[0] in ['join', 'order']:
            return cls._parse_join(tokens)
        elif tokens[0] == 'complement':
            return cls._parse_complement(tokens)
        raise ValueError('interval {} does not fit pattern.'.format(tokens))

    @classmethod
    def _parse_interval(cls, tokens):
        """ Parses a range
         Range ::= <num> | <num> ('..' | '^') <num>
        """
        fr = int(tokens.pop(0)) - 1
        if len(tokens) > 1 and tokens[0] in ['..', '^']:
            tokens.pop(0)  # Pop '..' | '^'
            to = int(tokens.pop(0))
            return GenomicInterval(None, fr, to)
        return GenomicInterval(None, fr, fr + 1)

    @classmethod
    def _parse_join(cls, tokens):
        """ Parses a join.
         Join ::= 'join' '(' SuperRange [',' SuperRange] ')'
        """
        res = []
        tokens.pop(0)  # Pop 'join'
        tokens.pop(0)  # Pop '('
        res.append(cls._parse_nested_interval(tokens))
        while tokens[0] == ',':
            tokens.pop(0)
            res.append(cls._parse_nested_interval(tokens))
        tokens.pop(0)  # Pop ')'
        return NestedGenomicInterval(res)

    @classmethod
    def _parse_complement(cls, tokens):
        """ Parses a complement
         Complement ::= 'complement' '(' SuperRange ')'
        """
        tokens.pop(0)  # Pop 'complement'
        tokens.pop(0)  # Pop '('
        res = cls._parse_nested_interval(tokens)
        tokens.pop(0)  # Pop ')'
        res.strand = '-' if res.strand == '+' else '+'
        return res

    def _iter_qualifiers(self, iterator):
        value = []
        for c, n in iterator:
            self.line_no += 1
            if c[21] == '/':
                if '=' in c:
                    key = c[22:c.find('=')]
                    value = [c[c.find('=') + 1:].strip()]
                else:
                    yield c[22:], True
                    if n[:21].strip() != '':
                        raise StopIteration
                    continue
            else:
                try:
                    value.append(c[21:])
                except AttributeError, e:
                    raise e

            if n[:21].strip() != '' or n[21] == '/':
                value = ''.join(value) if key == 'translation' else ' '.join(value)
                value = value.replace('"', '') if '"' in value else\
                    int(value) - 1 if key == 'codon_start' else\
                    int(value) if value.isdigit() else ''
                yield key, value
            if n[:21].strip() != '':
                raise StopIteration
