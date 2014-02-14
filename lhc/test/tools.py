from unittest import TestCase, main

from lhc.tools import enum, window

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
