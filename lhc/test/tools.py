from unittest import TestCase, main

from lhc.tools import enum, argsort, window

class TestTools(TestCase):
    def test_enum(self):
        values = enum(['A', 'B', 'C', 'D'])
        
        self.assertIn('A', values)
        self.assertIn('B', values)
        self.assertIn('C', values)
        self.assertIn('D', values)
        
        self.assertEquals(values.A, 'A')
        self.assertEquals(values.B, 'B')
        self.assertEquals(values.C, 'C')
        self.assertEquals(values.D, 'D')
        
        self.assertEquals(values['A'], 'A')
        self.assertEquals(values['B'], 'B')
        self.assertEquals(values['C'], 'C')
        self.assertEquals(values['D'], 'D')
    
    def test_argsort(self):
        values = [9, 8, 1, 2, 7, 6, 3, 4, 5]
        
        res = argsort(values)
        
        self.assertEquals(res, [2, 3, 6, 7, 8, 5, 4, 1, 0])
    
    def test_argsortInterval(self):
        from lhc.binf.genomic_coordinate import Interval
        values = [Interval('1', 10, 20), Interval('1', 5, 15), Interval('1', 15, 25)]
        
        res = argsort(values)
        
        self.assertEquals(res, [1, 0, 2])

    def test_windowWinltSeq(self):
        seq = 'atacgtagt'
        
        res = list(window(seq, 2, lambda x: ''.join(x)))
        
        self.assertEquals(res, ['at', 'ta', 'ac', 'cg', 'gt', 'ta', 'ag', 'gt'])
    
    def test_windowWingtSeq(self):
        seq = 'atacgtagtt'
        
        self.assertRaises(ValueError, next, window(seq, 20))

if __name__ == '__main__':
    import sys
    sys.exit(main())
