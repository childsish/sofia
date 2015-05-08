import string

from collections import namedtuple
from entity import Entity, Column
from lhc.interval import Interval


class EntityParser(object):
    """
    <entity> ::= (<name>.)?<type><definition>
    <definition> ::= <column> | [<entity>(,<entity>)*]
    <name> ::= [a-zA-Z_]+
    <type> ::= [a-zA-Z]+
    <column> ::= [0-9]+
    """

    NAME_AND_TYPE = frozenset(string.ascii_letters + '_.')
    TYPES = {
        's': str, 'i': int, 'f': float, 'v': Interval
    }

    def __init__(self):
        self.start = None
        self.stop = None

    def parse_definition(self, definition):
        self.start = 0
        self.stop = len(definition)
        res = self._parse_definition(definition)
        res = res[0] if len(res) == 1 else\
            Entity(namedtuple('Entry', [('V{}'.format(i + 1) if r.name is None else r.name) for i, r in enumerate(res)]),
                   res, 'Entry')
        return res

    def _parse_definition(self, definition):
        res = []
        while self.start < self.stop:
            pos = self.start
            while self.start < self.stop and definition[self.start] in self.NAME_AND_TYPE:
                self.start += 1
            name, type = ([None] + definition[pos:self.start].split('.', 1))[-2:]
            type = self.TYPES[type]
            if definition[self.start] == '[':
                self.start += 1
                self.stop -= 1
                entities = self._parse_definition(definition)
                res.append(Entity(type, entities, name))
            elif definition[self.start].isdigit():
                pos = self.start
                while self.start < self.stop and definition[self.start].isdigit():
                    self.start += 1
                column = int(definition[pos:self.start])
                res.append(Column(type, column, name))
            else:
                raise ValueError('invalid entity definition: {}'.format(definition))

            if self.start < len(definition) and definition[self.start] == ',':
                self.start += 1
        return res

    @classmethod
    def register_type(cls, code, type):
        if code in cls.TYPES:
            raise KeyError('type code "{}" already taken'.format(code))
        cls.TYPES[code] = type
