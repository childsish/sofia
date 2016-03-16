import unittest
from StringIO import StringIO

from lhc.io.fasta_.tools.wrap import wrap_input


class TestWrap(unittest.TestCase):
    def setUp(self):
        self.in_fhndl = StringIO('>chr1\naaccggtt\naaccggtt\naa\n>chr2\naaacccgggtttt\naaacccgggtttt\na')

    def test_wrap_input(self):
        it = wrap_input(self.in_fhndl, 20, 4)

        self.assertEquals('', it.next())
        self.assertEquals('>chr1', it.next())
        self.assertEquals('aacc', it.next())
        self.assertEquals('ggtt', it.next())
        self.assertEquals('aacc', it.next())
        self.assertEquals('ggtt', it.next())
        self.assertEquals('aa', it.next())
        self.assertEquals('>chr2', it.next())
        self.assertEquals('aaac', it.next())
        self.assertEquals('ccgg', it.next())
        self.assertEquals('gttt', it.next())
        self.assertEquals('taaa', it.next())
        self.assertEquals('cccg', it.next())
        self.assertEquals('ggtt', it.next())
        self.assertEquals('tta', it.next())
