import string

from collections import namedtuple
from entity import Entity, Column
from lhc.interval import Interval


class EntityParser(object):
    """
    Grammar
    -------
    <entity> ::= ( <name> "-" )? <type> <definition>
    <definition> ::= <column> | "[" <entity> ("." <entity>)* "]"
    <name> ::= [a-zA-Z_]+
    <type> ::= [a-zA-Z]+
    <column> ::= [0-9]+  # 1-indexed

    Examples
    --------
    s1       - create a string using column 1.
    r[i2.i3] - create integers from columns 2 and 3 then create an interval from the integers
    chr-s1.pos-i4

    Notes
    -----
    * Can not use ',' in windows command lines.
    """

    NAME_AND_TYPE = frozenset(string.ascii_letters + '_-')
    TYPES = {
        's': str,  # (s)tring
        'i': int,  # (i)nteger
        'f': float,  # (f)loat
        'r': Interval  # (r)ange
    }
    NAME_DELIMITER = '-'
    FIELD_DELIMITER = '.'
    OPEN_SUBENTITY = '['
    CLOSE_SUBENTITY = ']'

    def __init__(self):
        self.pos = None

    def parse_definition(self, definition):
        self.pos = 0
        res = self._parse_definition(definition)
        res = res[0] if len(res) == 1 else\
            Entity(namedtuple('Entry', [('V{}'.format(i + 1) if r.name is None else r.name)
                                        for i, r in enumerate(res)]),
                   res, 'Entry')
        return res

    def _parse_definition(self, definition):
        res = []
        while self.pos < len(definition):
            fr = self.pos
            while self.pos < len(definition) and definition[self.pos] in self.NAME_AND_TYPE:
                self.pos += 1
            name, type = ([None] + definition[fr:self.pos].split(self.NAME_DELIMITER, 1))[-2:]
            type = self.TYPES[type]
            if definition[self.pos] == self.OPEN_SUBENTITY:
                self.pos += 1
                entities = self._parse_definition(definition)
                res.append(Entity(type, entities, name))
                if self.pos >= len(definition):
                    raise ValueError('premature ending in definition; {}'.format(definition))
                self.pos += 1
            elif definition[self.pos].isdigit():
                fr = self.pos
                while self.pos < len(definition) and definition[self.pos].isdigit():
                    self.pos += 1
                column = int(definition[fr:self.pos])
                res.append(Column(type, column - 1, name))
            else:
                raise ValueError('invalid entity definition: {}. Expected {} or a digit at position {}.'.format(
                    definition, self.OPEN_SUBENTITY, self.pos))

            if self.pos < len(definition):
                if definition[self.pos] == self.FIELD_DELIMITER:
                    self.pos += 1
                elif definition[self.pos] == self.CLOSE_SUBENTITY:
                    break
                else:
                    raise ValueError('invalid entity definition: {}. Expected either {} or {} at position {}.'.format(
                        definition, self.FIELD_DELIMITER, self.CLOSE_SUBENTITY, self.pos))
        return res

    @classmethod
    def register_type(cls, code, type):
        if code in cls.TYPES:
            raise KeyError('type code "{}" already taken'.format(code))
        cls.TYPES[code] = type
