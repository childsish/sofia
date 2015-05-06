import re

from collections import namedtuple
from entry_builder import EntryBuilder
from lhc.interval import Interval


class EntryBuilderParser(object):

    TYPES = {
        'string': str, 'str': str, 's': str,
        'integer': int, 'int': int, 'i': int,
        'float': float, 'f': float,
        'interval': Interval, 'v': Interval
    }
    BUILDER_REGX = re.compile('((?P<name>\w[\w\d_]):)?(?P<definition>\w+\d+[\d,]+])')
    ENTITY_REGX = re.compile('(?P<type>\w+)(?P<columns>\d+[\d,]+])')

    def parse_builders(self, definitions):
        names, builders = zip(*[self.parse_builder(definition) for definition in definitions])
        return EntryBuilder(namedtuple('Entry', names), builders)

    def parse_builder(self, definition):
        match = self.BUILDER_REGX.match(definition)
        if match is None:
            raise ValueError('Invalid builder definition: {}'.format(definition))
        name = match.group('name')
        builder = self.parse_entity(match.group('definition'))
        return name, builder

    def parse_entity(self, definition):
        match = self.ENTITY_REGX.match(definition)
        if match is None:
            raise ValueError('Invalid entity definition: {}'.format(definition))
        type = match.group('type')
        columns = [int(col) for col in match.group('columns').split(',')]
        return EntryBuilder(self.TYPES[type], columns=columns)

    @classmethod
    def register_type(cls, code, type):
        if code in cls.TYPES:
            raise KeyError('type code "{}" already taken'.format(code))
        cls.TYPES[code] = type
