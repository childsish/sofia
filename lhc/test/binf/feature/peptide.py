from unittest import TestCase, main

from lhc.binf.genetic_code import GeneticCodes
from lhc.binf.feature.peptide import PeptideFrequency

class TestPeptideFrequency(TestCase):
    def test_generate(self):
        gcs = GeneticCodes('/data/gc.prt')
        gen = PeptideFrequency(gcs['Standard'])
        seq = 'cttatagcgatg'

        res = gen.generate(gen.transform(seq))
        
        self.assertEquals(res.items(), [
            ('A', 1), ('C', 0), ('E', 0), ('D', 0), ('G', 0), ('F', 0),
            ('I', 1), ('H', 0), ('K', 0), ('M', 1), ('L', 1), ('N', 0),
            ('Q', 0), ('P', 0), ('S', 0), ('R', 0), ('T', 0), ('W', 0),
            ('V', 0), ('Y', 0), ('X', 0)
        ])
    
    def test_noStop(self):
        gcs = GeneticCodes('/data/gc.prt')
        gen = PeptideFrequency(gcs['Standard'])
        seq = 'cttatagcgatgtaa'

        res = gen.generate(gen.transform(seq))
        
        self.assertNotIn('*', res)
        
if __name__ == '__main__':
    import sys
    sys.exit(main())
