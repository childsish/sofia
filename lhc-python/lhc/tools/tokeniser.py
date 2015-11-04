__author__ = 'Liam Childs'

from collections import namedtuple

Token = namedtuple('Token', ('type', 'value'))


class Tokeniser(object):
    def __init__(self, types):
        self._type_map = {}
        for type, characters in types.iteritems():
            for character in characters:
                self._type_map[character] = type

    def tokenise(self, string):
        type_map = self._type_map

        fr = 0
        while fr < len(string):
            type = type_map[string[fr]]
            to = fr
            while to < len(string) and type == type_map[string[to]]:
                to += 1
            yield Token(type=type, value=string[fr:to])
            fr = to
