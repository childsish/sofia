__author__ = 'Liam Childs'

import os
import tempfile
import unittest

from lhc.io.vcf_.iterator import VcfEntryIterator
from lhc.io.vcf_.set_ import VcfSet


class TestSet(unittest.TestCase):
    def setUp(self):
        fhndl, self.fname = tempfile.mkstemp()
        os.write(fhndl, '##VCF=2.0\n'\
            '#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\ts1\n'\
            'chr1\t101\ta0\ta\tt\t40\tPASS\tGT=5\tGT:GQ\t0/1:100.0\n'\
            'chr1\t201\ta1\tg\tc\t40\tPASS\tGT=5\tGT:GQ\t0/1:100.0\n'\
            'chr1\t301\ta2\tt\tc\t40\tPASS\tGT=5\tGT:GQ\t0/1:100.0\n'\
            'chr1\t401\ta3\ttACG\tt\t40\tPASS\tGT=5\tGT:GQ\t0/1:100.0\n'\
            'chr1\t501\ta4\tc\tcAAG\t40\tPASS\tGT=5\tGT:GQ\t0/1:100.0\n')
        os.close(fhndl)

    def test_getItemByPos(self):
        parser = VcfSet(VcfEntryIterator(open(self.fname)))

        var = parser.fetch('chr1', 100)
        self.assertEquals(len(var), 1)
        var = var[0]
        self.assertEquals('chr1', var.chr)
        self.assertEquals(100, var.pos)
        self.assertEquals('a0', var.id)
        self.assertEquals('a', var.ref)
        self.assertEquals('t', var.alt)
        self.assertEquals(40, var.qual)
        self.assertEquals('PASS', var.filter)
        self.assertEquals({'GT': '5'}, var.info)

    def test_getItemByInterval(self):
        parser = VcfSet(VcfEntryIterator(open(self.fname)))

        vars = parser.fetch('chr1', 50, 150)
        self.assertEquals(len(vars), 1)
        self.assertEquals(vars[0].id, 'a0')

        vars = parser.fetch('chr1', 50, 250)
        self.assertEquals(len(vars), 2)
        self.assertEquals(set(var.id for var in vars), {'a0', 'a1'})


if __name__ == '__main__':
    unittest.main()
