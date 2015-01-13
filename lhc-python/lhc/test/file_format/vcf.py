import os
import tempfile
import unittest

from subprocess import Popen
from lhc.binf.genomic_coordinate import Position, Interval
from lhc.file_format.vcf_.iterator import VcfIterator
from lhc.file_format.vcf_.set_ import VcfSet

class TestVcf(unittest.TestCase):
    
    def setUp(self):
        fhndl, self.fname = tempfile.mkstemp()
        os.write(fhndl, 'chr1\t101\ta0\ta\tt\t40\tPASS\tGT=5\tGT:GQ\t0/1:100.0\n'\
            'chr1\t201\ta1\tg\tc\t40\tPASS\tGT=5\tGT:GQ\t0/1:100.0\n'\
            'chr1\t301\ta2\tt\tc\t40\tPASS\tGT=5\tGT:GQ\t0/1:100.0\n'\
            'chr1\t401\ta3\ttACG\tt\t40\tPASS\tGT=5\tGT:GQ\t0/1:100.0\n'\
            'chr1\t501\ta4\tc\tcAAG\t40\tPASS\tGT=5\tGT:GQ\t0/1:100.0\n')
        os.close(fhndl)

        prc_stdout = open('%s.sorted'%self.fname, 'w')
        prc_stdout.write('##fileformat=VCFv4.1\n'\
            '#CHR\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\tsample1\n')
        prc_stdout.flush()
        prc = Popen(['sort', '-k1,1', '-k2,2n', self.fname], stdout=prc_stdout)
        prc.wait()
        prc_stdout.close()
        prc = Popen(['mv', '%s.sorted'%self.fname, self.fname])
        prc.wait()

        prc = Popen(['bgzip', self.fname])
        prc.wait()
        prc = Popen(['tabix', '-p', 'vcf', '%s.gz'%self.fname])
        prc.wait()
    
    def test_iterEntries(self):
        it = VcfIterator('%s.gz'%self.fname)
        
        var = it.next()
        self.assertEquals(var.chr, 'chr1')
        self.assertEquals(var.pos, 100)
        self.assertEquals(var.id, 'a0')
        self.assertEquals(var.ref, 'a')
        self.assertEquals(var.alt, 't')
        self.assertEquals(var.qual, '40')
        self.assertEquals(var.filter, 'PASS')
        self.assertEquals(var.info, {'GT': '5'})
        self.assertEquals(var.samples, {'sample1': {'GT': '0/1', 'GQ': '100.0'}})
        self.assertEquals(it.next().id, 'a1')
        self.assertEquals(it.next().id, 'a2')
        self.assertEquals(it.next().id, 'a3')
        self.assertEquals(it.next().id, 'a4')
        self.assertRaises(StopIteration, it.next)
    
    def test_getItemByPos(self):
        parser = VcfSet(VcfIterator('%s.gz'%self.fname))
        
        var = parser[Position('chr1', 100)]
        self.assertEquals(len(var), 1)
        var = var[0]
        self.assertEquals(var.chr, 'chr1')
        self.assertEquals(var.pos, 100)
        self.assertEquals(var.id, 'a0')
        self.assertEquals(var.ref, 'a')
        self.assertEquals(var.alt, 't')
        self.assertEquals(var.qual, '40')
        self.assertEquals(var.filter, 'PASS')
        self.assertEquals(var.info, {'GT': '5'})
     
    def test_getItemByInterval(self):
        parser = VcfSet(VcfIterator('%s.gz'%self.fname))
        
        vars = parser[Interval('chr1', 50, 150)]
        self.assertEquals(len(vars), 1)
        self.assertEquals(vars[0].id, 'a0')
        
        vars = parser[Interval('chr1', 50, 250)]
        self.assertEquals(len(vars), 2)
        self.assertEquals(set(var.id for var in vars), set(('a0', 'a1')))
    
    def tearDown(self):
        os.remove('%s.gz'%self.fname)
        os.remove('%s.gz.tbi'%self.fname)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())

