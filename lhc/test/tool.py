from unittest import TestCase, main

from lhc.tool import window

class TestWindow(TestCase):
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
