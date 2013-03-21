from unittest import TestCase, main

from lhc.binf.genetic_code import GeneticCodes
from lhc.binf.feature.codon import CodonUsage, CodonAdaptationIndex, EffectiveNumberOfCodons
from lhc.file_format.cut import readCodonUsageTable

class TestCodonUsage(TestCase):
    def test_generate(self):
        seq = 'cttatagcgatg'
        gen = CodonUsage()
        
        res = gen.generate(seq)
    
        self.assertEquals([x for x in res.iteritems() if x[1] != 0],\
            [('ata', 1), ('atg', 1), ('ctt', 1), ('gcg', 1)])

    def test_withRedundant(self):
        seq = 'ctyatagcgatg'
        gen = CodonUsage(False)
        
        res = gen.generate(seq)
    
        self.assertIn('cty', res)

    def test_withoutRedundant(self):
        seq = 'ctyatagcgatg'
        gen = CodonUsage(True)
        
        res = gen.generate(seq)
    
        self.assertNotIn('cty', res)

class TestCodonAdaptationIndex(TestCase):
    def test_generate(self):
        gcs = GeneticCodes()
        cut = readCodonUsageTable('/data/organisms/Ath/cut.txt')
        gen = CodonAdaptationIndex(gcs['Standard'], cut)
        seq = 'cttatagcgatg'
        
        res = gen.generate(seq)
        
        self.assertAlmostEqual(res['cai'], 0.57180187)

class TestEffectiveNumberOfCodons(TestCase):
    def test_calculate(self):
        gcs = GeneticCodes()
        gen = EffectiveNumberOfCodons(gcs['Standard'])
        seq = 'ATGGAGGATCAAGTTGGGTTTGGGTTCCGTCCGAACGACGAGGAGCTCGTTGGTCACTATCTCCGTAACAAAATCGAAGGAAACACTAGCCGCGACGTTGAAGTAGCCATCAGCGAGGTCAACATCTGTAGCTACGATCCTTGGAACTTGCGCTTCCAGTCAAAGTACAAATCGAGAGATGCTATGTGGTACTTCTTCTCTCGTAGAGAAAACAACAAAGGGAATCGACAGAGCAGGACAACGGTTTCTGGTAAATGGAAGCTTACCGGAGAATCTGTTGAGGTCAAGGACCAGTGGGGATTTTGTAGTGAGGGCTTTCGTGGTAAGATTGGTCATAAAAGGGTTTTGGTGTTCCTCGATGGAAGATACCCTGACAAAACCAAATCTGATTGGGTTATCCACGAGTTCCACTACGACCTCTTACCAGAACATCAGAGGACATATGTCATCTGCAGACTTGAGTACAAGGGTGATGATGCGGACATTCTATCTGCTTATGCAATAGATCCCACTCCCGCTTTTGTCCCCAATATGACTAGTAGTGCAGGTTCTGTGGTCAACCAATCACGTCAACGAAATTCAGGATCTTACAACACTTACTCTGAGTATGATTCAGCAAATCATGGCCAGCAGTTTAATGAAAACTCTAACATTATGCAGCAGCAACCACTTCAAGGATCATTCAACCCTCTCCTTGAGTATGATTTTGCAAATCACGGCGGTCAGTGGCTGAGTGACTATATCGACCTGCAACAGCAAGTTCCTTACTTGGCACCTTATGAAAATGAGTCGGAGATGATTTGGAAGCATGTGATTGAAGAAAATTTTGAGTTTTTGGTAGATGAAAGGACATCTATGCAACAGCATTACAGTGATCACCGGCCCAAAAAACCTGTGTCTGGGGTTTTGCCTGATGATAGCAGTGATACTGAAACTGGATCAATGATTTTCGAAGACACTTCGAGCTCCACTGATAGTGTTGGTAGTTCAGATGAACCGGGCCATACTCGTATAGATGATATTCCATCATTGAACATTATTGAGCCTTTGCACAATTATAAGGCACAAGAGCAACCAAAGCAGCAGAGCAAAGAAAAGGTGATAAGTTCGCAGAAAAGCGAATGCGAGTGGAAAATGGCTGAAGACTCGATCAAGATACCTCCATCCACCAACACGGTGAAGCAGAGCTGGATTGTTTTGGAGAATGCACAGTGGAACTATCTCAAGAACATGATCATTGGTGTCTTGTTGTTCATCTCCGTCATTAGTTGGATCATTCTTGTTGGTTAA'
        
        res = gen.generate(gen.transform(seq))
        
        print res

if __name__ == '__main__':
    import sys
    sys.exit(main())
