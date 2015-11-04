from collections import namedtuple
from lhc.interval import Interval
from lhc.tools.tokeniser import Tokeniser, Token
from formatters import ColumnFormatter, EntityFormatter


class FormatParser(object):
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
    s1            - create a string using column 1.
    r[i2.i3]      - create integers from columns 2 and 3 then create an interval from the integers
    chr-s1.pos-i4 - create a namedtuple with the fields chr and pos, where pos is an integer

    Notes
    -----
     * Can not use ',' in windows command lines.
     * ':' can be used by other tools as a delimiter.
    """

    def __init__(self):
        self._tokeniser = Tokeniser({
            'word': 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_',
            'number': '0123456789',
            'open_subentity': '[',
            'close_subentity': ']',
            'name_delimiter': '-',
            'field_delimiter': '.'
        })
        self._types = {
            's': str,
            'i': int,
            'f': float,
            'r': Interval
        }

    def parse(self, definition):
        tokens = list(self._tokeniser.tokenise(definition))
        formatters = []
        i = 0
        while True:
            formatter = self.parse_entity(tokens)
            if formatter.name == '':
                formatter.name = 'V{}'.format(i + 1)
            formatters.append(formatter)
            i += 1

            if len(tokens) == 0:
                break
            next = tokens.pop(0)
            if next.type != 'field_delimiter':
              raise ValueError('invalid token. expected ".", got: "{}"'.format(next.value))
        if len(formatters) == 1:
            return formatters[0]
        return EntityFormatter(namedtuple('Entry', [formatter.name for formatter in formatters]), formatters, 'Entry')

    def parse_entity(self, tokens):
        name = Token(type='word', value='')
        type = tokens.pop(0)
        if tokens[0].type == 'name_delimiter':
            name = type
            tokens.pop(0)
            type = tokens.pop(0)
        next = tokens.pop(0)
        if next.type == 'number':
            return ColumnFormatter(self._types[type.value], int(next.value) - 1, name.value)
        elif next.type == 'open_subentity':
            formatters = [self.parse_entity(tokens)]
            while len(tokens) > 0 and tokens[0].type == 'field_delimiter':
                tokens.pop(0)
                formatters.append(self.parse_entity(tokens))
            if len(tokens) == 0:
                raise ValueError('unexpected end of definition')
            elif tokens[0].type != 'close_subentity':
                raise ValueError('invalid token. expected "]", got: "{}"'.format(tokens[0].value))
            tokens.pop(0)
            return EntityFormatter(self._types[type.value], formatters, name.value);
        raise ValueError('invalid token. expected a number or "[", got: "{}"'.format(next.value))

    def register_type(self, code, type):
        if code in self._types:
            raise KeyError('type code "{}" already taken'.format(code))
        self._types[code] = type
