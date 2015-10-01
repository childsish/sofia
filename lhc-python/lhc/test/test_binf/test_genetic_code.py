from unittest import TestCase, main

from lhc.binf.genetic_code import GeneticCodes


class TestGeneticCodes(TestCase):
    def test_integration(self):
        gc = GeneticCodes()

        self.assertIn('Standard', gc.name2id)
        self.assertEquals(gc['Standard']['ttt'], 'F')
        self.assertEquals(gc['Standard']['ggg'], 'G')

if __name__ == '__main__':
    import sys
    sys.exit(main())
