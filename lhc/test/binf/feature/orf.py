from unittest import TestCase, main
from lhc.binf.feature.orf import ORFNumber

class TestORFNumber(TestCase):
    def test_generate(self):
        seq = 'ccccccatgcatgcatgcccctaactagcccc'
        gen = ORFNumber()
        
        res = gen.generate(seq)

        self.assertEquals(res, {'norf': 2})

if __name__ == '__main__':
    import sys
    sys.exit(main())
