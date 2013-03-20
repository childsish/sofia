from collections import Counter
from unittest import TestCase, main
from lhc.binf.pest import Pest

class TestPest(TestCase):
    def test_iterCandidates(self):
        seq = 'AAAAAAAAAAAARRRRAAAAAAAAAAAAKRHRKHRKAAAAAAAAAAAAKK'
        pest = Pest()
        
        res = list(pest.iterCandidates(seq))
        
        self.assertEquals(res, [(0, 12), (16, 28), (36, 48)])
    
    def test_isValidPestTrue(self):
        pest = Pest()
        
        self.assertTrue(pest.isValidPest(Counter('PDSAAAAAAAAA')))
        self.assertTrue(pest.isValidPest(Counter('PDTAAAAAAAAA')))
        self.assertTrue(pest.isValidPest(Counter('PESAAAAAAAAA')))
        self.assertTrue(pest.isValidPest(Counter('PETAAAAAAAAA')))

    def test_isValidPestFalse(self):
        pest = Pest()
        
        self.assertFalse(pest.isValidPest(Counter('PDAAAAAAAAAA')))
        self.assertFalse(pest.isValidPest(Counter('PSAAAAAAAAAA')))
        self.assertFalse(pest.isValidPest(Counter('DSAAAAAAAAAA')))
    
    def test_iterPest(self):
        seq = 'PDSAAAAAAAAARRRRPDTAAAAAAAAAKRHPESKHRKPETAAAAAAAAAKK'
        pest = Pest()
        
        res = list(pest.iterPest(seq))
        
        self.assertAlmostEquals(res[0][0], -24.8835503)
        self.assertEquals(res[0][1], (0, 12))
        self.assertAlmostEquals(res[1][0], -24.8802297)
        self.assertEquals(res[1][1], (16, 28))
        self.assertAlmostEquals(res[2][0], -24.5838916)
        self.assertEquals(res[2][1], (38, 50))

if __name__ == '__main__':
    import sys
    sys.exit(main())
