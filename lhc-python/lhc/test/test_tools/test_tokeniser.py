__author__ = 'Liam Childs'

import string
import unittest

from lhc.tools.tokeniser import Tokeniser


class TestTokeniser(unittest.TestCase):
    def test_tokeniser(self):
        tokeniser = Tokeniser({
            'number': '0123456789',
            'word': string.letters,
            'space': ' '
        })

        tokens = list(tokeniser.tokenise('19 out of 20'))

        self.assertEquals(7, len(tokens))
        self.assertEquals('number', tokens[0].type)
        self.assertEquals('19', tokens[0].value)
        self.assertEquals('space', tokens[1].type)
        self.assertEquals(' ', tokens[1].value)
        self.assertEquals('word', tokens[2].type)
        self.assertEquals('out', tokens[2].value)
        self.assertEquals('space', tokens[3].type)
        self.assertEquals(' ', tokens[3].value)
        self.assertEquals('word', tokens[4].type)
        self.assertEquals('of', tokens[4].value)
        self.assertEquals('space', tokens[5].type)
        self.assertEquals(' ', tokens[5].value)
        self.assertEquals('number', tokens[6].type)
        self.assertEquals('20', tokens[6].value)


if __name__ == '__main__':
    unittest.main()
