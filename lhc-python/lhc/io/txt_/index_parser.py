import re

from lhc.indices import KeyIndex, IntervalIndex


class IndexParser(object):

    REGX = re.compile('(?P<code>\w+)(?P<column>\d+)')
    INDICES = {
        'k': KeyIndex,  # (k)ey index
        'i': IntervalIndex,  # (i)nterval index
    }

    def parse_definition(self, definition):
        match = self.REGX.match(definition)
        if not match:
            raise ValueError('invalid index definition: {}'.format(definition))
        return self.INDICES[match.group('code')], int(match.group('column'))

    @classmethod
    def register_index(cls, code, index):
        cls.INDICES[code] = index
