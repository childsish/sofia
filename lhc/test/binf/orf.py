from unittest import TestCase, main

from lhc.binf.orf import findORFs

class TestFindORFs(TestCase):
    def test_findORFs(self):
        seq = 'ccccccatgcatgcatgcccctaactagcccc'
        
        res = findORFs(seq)
        
        self.assertEquals(res, ['atgcatgcatgcccctaa', 'atgcatgcccctaactag'])

if __name__ == '__main__':
    import sys
    sys.exit(main())
