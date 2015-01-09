from unittest import TestCase, main
from lhc.binf.aa import readMolWeight

class TestReadMolWt(TestCase):
    def test_noFilename(self):
        res = readMolWeight()
        
        self.assertAlmostEqual(res['A']['avg'], 71.0788)

if __name__ == '__main__':
    import sys
    sys.exit(main())
