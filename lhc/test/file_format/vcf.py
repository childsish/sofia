import os
import tempfile
import unittest

from lhc.binf.genomic_coordinate import Position, Interval
from lhc.file_format import vcf

class TestVcf(unittest.TestCase):
    
    def setUp(self):
        fhndl, self.fname = tempfile.mkstemp()
        os.write(fhndl, '#CHR\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tATTR\n' +
            'chr1\t101\ta0\ta\tt\t40\tPASS\tGT:5\n' +
            'chr1\t201\ta1\tg\tc\t40\tPASS\tGT:5\n' +
            'chr1\t301\ta2\tt\tc\t40\tPASS\tGT:5\n' +
            'chr1\t401\ta3\ttACG\tt\t40\tPASS\tGT:5\n' +
            'chr1\t501\ta4\tc\tcAAG\t40\tPASS\tGT:5\n')
        os.close(fhndl)
    
    def test_iterEntries(self):
        it = vcf.iterEntries(self.fname)
        
        var = it.next()
        self.assertEquals(var.chr, 'chr1')
        self.assertEquals(var.pos, 100)
        self.assertEquals(var.id, 'a0')
        self.assertEquals(var.ref, 'a')
        self.assertEquals(var.alt, 't')
        self.assertEquals(var.qual, 40)
        self.assertEquals(var.filter, 'PASS')
        self.assertEquals(var.attr, {'GT': '5'})
        self.assertEquals(it.next().id, 'a1')
        self.assertEquals(it.next().id, 'a2')
        self.assertEquals(it.next().id, 'a3')
        self.assertEquals(it.next().id, 'a4')
        self.assertRaises(StopIteration, it.next)
    
    def test_getItemByPos(self):
        parser = vcf.VcfParser(self.fname)
        
        var = parser[Position('chr1', 100)]
        self.assertEquals(var.chr, 'chr1')
        self.assertEquals(var.pos, 100)
        self.assertEquals(var.id, 'a0')
        self.assertEquals(var.ref, 'a')
        self.assertEquals(var.alt, 't')
        self.assertEquals(var.qual, 40)
        self.assertEquals(var.filter, 'PASS')
        self.assertEquals(var.attr, {'GT': '5'})
     
    def test_getItemByInterval(self):
        parser = vcf.VcfParser(self.fname)
        
        vars = parser[Interval('chr1', 50, 150)]
        self.assertEquals(len(vars), 1)
        self.assertEquals(vars[0].id, 'a1')
        
        vars = parser[Interval('chr1', 50, 250)]
        self.assertEquals(len(vars), 2)
        self.assertEquals(set(var.id for var in vars), set(('a0', 'a1')))
 
    def test_getItemIndexedByPos(self):
        vcf.index(self.fname)
        parser = vcf.VcfParser(self.fname)
        
        var = parser[Position('chr1', 100)]
        self.assertEquals(var.chr, 'chr1')
        self.assertEquals(var.pos, 100)
        self.assertEquals(var.id, 'a0')
        self.assertEquals(var.ref, 'a')
        self.assertEquals(var.alt, 't')
        self.assertEquals(var.qual, 40)
        self.assertEquals(var.filter, 'PASS')
        self.assertEquals(var.attr, {'GT': '5'})
    
    def test_getItemIndexedInterval(self):
        vcf.index(self.fname)
        parser = vcf.VcfParser(self.fname)
        
        vars = parser[Interval('chr1', 50, 150)]
        self.assertEquals(len(vars), 1)
        self.assertEquals(vars[0].id, 'a1')
        
        vars = parser[Interval('chr1', 50, 250)]
        self.assertEquals(len(vars), 2)
        self.assertEquals(set(var.id for var in vars), set(('a0', 'a1')))
    
    def tearDown(self):
        os.remove(self.fname)
