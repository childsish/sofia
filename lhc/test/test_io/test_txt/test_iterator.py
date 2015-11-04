import os
import tempfile
import unittest

from lhc.io.txt_ import Iterator


class TestITerator(unittest.TestCase):
    def setUp(self):
        self.comment = ['#version=1.0\n',
                        '#date=010101\n']
        self.header = 'chr\tstart\tstop\tgene\n'
        self.data = ['chr1\t10\t20\ta\n',
                     'chr1\t30\t60\tb\n',
                     'chr1\t100\t110\tc\n',
                     'chr2\t15\t30\td\n',
                     'chr2\t40\t50\te\n',
                     'chr3\t10\t110\tf\n']

    def test_iterator(self):
        fhndl, fname = tempfile.mkstemp()
        os.write(fhndl, ''.join(self.comment))
        os.write(fhndl, ''.join(self.header))
        os.write(fhndl, ''.join(self.data))
        os.close(fhndl)

        lines = list(Iterator(open(fname), has_header=True))

        self.assertEquals(9, len(lines))
        self.assertEquals('comment', lines[0].type)
        self.assertEquals(self.comment[0], lines[0].value)
        self.assertEquals('comment', lines[1].type)
        self.assertEquals(self.comment[1], lines[1].value)
        self.assertEquals('header', lines[2].type)
        self.assertEquals(self.header, lines[2].value)
        self.assertEquals('line', lines[3].type)
        self.assertEquals(self.data[0], lines[3].value)
        self.assertEquals('line', lines[4].type)
        self.assertEquals(self.data[1], lines[4].value)
        self.assertEquals('line', lines[5].type)
        self.assertEquals(self.data[2], lines[5].value)
        self.assertEquals('line', lines[6].type)
        self.assertEquals(self.data[3], lines[6].value)
        self.assertEquals('line', lines[7].type)
        self.assertEquals(self.data[4], lines[7].value)
        self.assertEquals('line', lines[8].type)
        self.assertEquals(self.data[5], lines[8].value)


if __name__ == '__main__':
    unittest.main()
