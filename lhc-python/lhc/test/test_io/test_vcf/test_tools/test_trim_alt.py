__author__ = 'Liam Childs'

import unittest

from lhc.io.vcf_.tools.trim_alt import _trim_alt as trim_alt

class TestAltTrim(unittest.TestCase):
    def test_trim_alt(self):
        self.assertEquals(([1], ['T'], ['G']), trim_alt(1, 'T', 'G'))
        self.assertEquals(([1], ['T'], ['TGG']), trim_alt(1, 'T', 'TGG'))
        self.assertEquals(([1], ['TGG'], ['T']), trim_alt(1, 'TGG', 'T'))
        self.assertEquals(([1], ['T'], ['TG']), trim_alt(1, 'TG', 'TGG'))
        self.assertEquals(([1], ['TG'], ['T']), trim_alt(1, 'TGG', 'TG'))
        self.assertEquals(([1], ['T'], ['TA']), trim_alt(1, 'TGG', 'TAGG'))
        self.assertEquals(([1], ['T'], ['TGGA']), trim_alt(1, 'TGG', 'TGGAGG'))
        self.assertEquals(([3], ['A'], ['AGG']), trim_alt(1, 'TGA', 'TGAGG'))
        self.assertEquals(([3], ['G'], ['A']), trim_alt(1, 'TGG', 'TGA'))

    def test_trim_multiple_alt(self):
        self.assertEquals(([1, 1, 3], ['T', 'T', 'G'], ['TA', 'TGGA', 'A']), trim_alt(1, 'TGG', 'TAGG,TGGAGG,TGA'))
