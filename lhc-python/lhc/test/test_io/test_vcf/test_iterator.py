__author__ = 'Liam Childs'

import os
import tempfile
import unittest

from lhc.io.vcf_.iterator import VcfEntryIterator

class TestIterator(unittest.TestCase):
    
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
    
    def test_iterEntries(self):
        it = VcfEntryIterator(open(self.fname))
        
        var = it.next()
        self.assertEquals('chr1', var.chr)
        self.assertEquals(100, var.pos)
        self.assertEquals('a0', var.id)
        self.assertEquals('a', var.ref)
        self.assertEquals('t', var.alt)
        self.assertEquals(40, var.qual)
        self.assertEquals('PASS', var.filter)
        self.assertEquals({'GT': '5'}, var.info)
        self.assertEquals({'s1': {'GT': '0/1', 'GQ': '100.0'}}, var.samples)
        self.assertEquals('a1', it.next().id)
        self.assertEquals('a2', it.next().id)
        self.assertEquals('a3', it.next().id)
        self.assertEquals('a4', it.next().id)
        self.assertRaises(StopIteration, it.next)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
