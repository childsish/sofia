from unittest import TestCase, main
from lhc.binf.feature.rna import MinimumFreeEnergy, EnsembleFreeEnergy

class TestMinimumFreeEnergy(TestCase):
    def test_generate(self):
        seq = 'atattgcgcgcaatat'
        gen = MinimumFreeEnergy()
        
        res = gen.generate(seq)
        
        self.assertAlmostEquals(res['mfe'], -1.5)

class TestEnsembleFreeEnergy(TestCase):
    def test_generate(self):
        seq = 'atattgcgcgcaatat'
        gen = EnsembleFreeEnergy()

        res = gen.generate(seq)

        self.assertAlmostEquals(res['efe'], -1.86378586)

if __name__ == '__main__':
    import sys
    sys.exit(main())
