from unittest import TestCase, main

from lhc.binf.feature.nucleotide import NucleotideFrequency, NucleotideSkew

class TestNucleotideFrequency(TestCase):
    def test_generateMono(self):
        gen = NucleotideFrequency(1)
        seq = 'aaaaccccggggtttt'
        
        res = gen.generate(seq)
        
        self.assertEquals(res.items(), [('a', 4), ('c', 4), ('g', 4), ('t', 4)])
    
    def test_generateDi(self):
        gen = NucleotideFrequency(2)
        seq = 'tatgcagtcgatcgta'
        
        res = gen.generate(seq)
        
        self.assertEquals(res.items(), [
            ('aa', 0), ('ac', 0), ('ag', 1), ('at', 2),
            ('ca', 1), ('cc', 0), ('cg', 2), ('ct', 0),
            ('ga', 1), ('gc', 1), ('gg', 0), ('gt', 2),
            ('ta', 2), ('tc', 2), ('tg', 1), ('tt', 0)
        ])
    
    def test_withoutRedundant(self):
        gen = NucleotideFrequency(2, True)
        seq = 'ctaygcatgcta'
        
        res = gen.generate(seq)
        
        self.assertNotIn('ay', res)
        self.assertNotIn('yg', res)

    def test_withRedundant(self):
        gen = NucleotideFrequency(2, False)
        seq = 'ctaygcatgcta'
        
        res = gen.generate(seq)
        
        self.assertIn('ay', res)
        self.assertIn('yg', res)

class TestNucleotideSkew(TestCase):
    def test_generateAGgtTC(self):
        gen = NucleotideSkew()
        seq = 'aaatgggc'
        
        res = gen.generate(seq)
        
        self.assertEquals(res.items(), [('at_skew', 0.5), ('gc_skew', 0.5)])

    def test_generateAGltTC(self):
        gen = NucleotideSkew()
        seq = 'atttgccc'
        
        res = gen.generate(seq)
        
        self.assertEquals(res.items(), [('at_skew', -0.5), ('gc_skew', -0.5)])

    def test_generateAGeqTC(self):
        gen = NucleotideSkew()
        seq = 'aattggcc'
        
        res = gen.generate(seq)
        
        self.assertEquals(res.items(), [('at_skew', 0), ('gc_skew', 0)])

    def test_generateNoAT(self):
        gen = NucleotideSkew()
        seq = 'ggcc'
        
        res = gen.generate(seq)
        
        self.assertEquals(res.items(), [('at_skew', 0), ('gc_skew', 0)])

if __name__ == '__main__':
    import sys
    sys.exit(main())
