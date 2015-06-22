import string

from collections import namedtuple
from entity import Entity, Column
from lhc.interval import Interval


class EntityParser(object):
    """
    Grammar
    <entity> ::= (<name>.)?<type><definition>
    <definition> ::= <column> | "[" <entity> ("," <entity>)* "]"
    <name> ::= [a-zA-Z_]+
    <type> ::= [a-zA-Z]+
    <column> ::= [0-9]+  # 1-indexed

    Examples
    s1       - create a string using column 1.
    r[i2,i3] - create integers from columns 2 and 3 then create an interval from the integers
    """

    NAME_AND_TYPE = frozenset(string.ascii_letters + '_.')
    TYPES = {
        's': str,  # (s)tring
        'i': int,  # (i)nteger
        'f': float,  # (f)loat
        'r': Interval  # (r)ange
    }

    def __init__(self):
        self.pos = None

    def parse_definition(self, definition):
        self.pos = 0
        res = self._parse_definition(definition)
        res = res[0] if len(res) == 1 else\
            Entity(namedtuple('Entry', [('V{}'.format(i + 1) if r.name is None else r.name) for i, r in enumerate(res)]),
                   res, 'Entry')
        return res

    def _parse_definition(self, definition):
        res = []
        while self.pos < len(definition):
            fr = self.pos
            while self.pos < len(definition) and definition[self.pos] in self.NAME_AND_TYPE:
                self.pos += 1
            name, type = ([None] + definition[fr:self.pos].split('.', 1))[-2:]
            type = self.TYPES[type]
            if definition[self.pos] == '[':
                self.pos += 1
                entities = self._parse_definition(definition)
                res.append(Entity(type, entities, name))
                if self.pos >= len(definition):
                    raise ValueError('premature ending in definition; {}'.format(definition))
                elif definition[self.pos] != ']':
                    raise ValueError('expected "]" at position {}, found "{}"'.format(self.pos, definition[self.pos]))
                self.pos += 1
            elif definition[self.pos].isdigit():
                fr = self.pos
                while self.pos < len(definition) and definition[self.pos].isdigit():
                    self.pos += 1
                column = int(definition[fr:self.pos])
                res.append(Column(type, column, name))
            else:
                raise ValueError('invalid entity definition: {}'.format(definition))

            if self.pos < len(definition):
                if definition[self.pos] == ',':
                    self.pos += 1
                elif definition[self.pos] == ']':
                    break
        return res

    @classmethod
    def register_type(cls, code, type):
        if code in cls.TYPES:
            raise KeyError('type code "{}" already taken'.format(code))
        cls.TYPES[code] = type
