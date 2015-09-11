import unittest

try:
    from lhc.misc.performance_measures import *
    skip = False
except ImportError:
    skip = True


@unittest.skipIf(skip, 'unable to import numpy')
class TestAccuracyMeasures(unittest.TestCase):
    def test_specificity(self):
        self.assertAlmostEqual(0.5, specificity(tp=5, fn=5))
        
    def test_sensitivity(self):
        self.assertAlmostEqual(0.5, sensitivity(tn=5, fp=5))
    
    def test_ber(self):
        self.assertAlmostEqual(0, ber(10, 10, 0, 0))
        self.assertAlmostEqual(0, ber(10, 100, 0, 0))
        self.assertAlmostEqual(0, ber(100, 10, 0, 0))
        
        self.assertAlmostEqual(0.5, ber(10, 10, 10, 10))
        self.assertAlmostEqual(0.5, ber(10, 50, 50, 10))
        self.assertAlmostEqual(0.5, ber(50, 10, 10, 50))
        
        self.assertAlmostEqual(1, ber(0, 0, 10, 10))
    
    def test_mcc(self):
        self.assertAlmostEqual(1, mcc(10, 10, 0, 0))
        self.assertAlmostEqual(1, mcc(10, 100, 0, 0))
        self.assertAlmostEqual(1, mcc(100, 10, 0, 0))
        
        self.assertAlmostEqual(0, mcc(10, 10, 10, 10))
        self.assertAlmostEqual(0, mcc(10, 50, 50, 10))
        self.assertAlmostEqual(0, mcc(50, 10, 10, 50))
        
        self.assertAlmostEqual(-1, mcc(0, 0, 10, 10))
        self.assertAlmostEqual(-1, mcc(0, 0, 10, 100))
        self.assertAlmostEqual(-1, mcc(0, 0, 100, 10))
    
    def test_mse(self):
        self.assertAlmostEqual(0, mse([10, 20, 30, 40, 50], [10, 20, 30, 40, 50]))
        self.assertAlmostEqual(4, mse([10, 20, 30, 40, 50], [12, 18, 32, 38, 52]))
    
    def test_mui(self):
        self.assertAlmostEqual(0, mui([0, 0, 1, 1], [0, 0, 0, 0]))
        self.assertAlmostEqual(0.3112781, mui([0, 0, 1, 1], [0, 0, 0, 1]))
        self.assertAlmostEqual(0.3112781, mui([0, 0, 1, 1], [0, 0, 1, 0]))
        self.assertAlmostEqual(1, mui([0, 0, 1, 1], [0, 0, 1, 1]))
        self.assertAlmostEqual(0.3112781, mui([0, 0, 1, 1], [0, 1, 0, 0]))
        self.assertAlmostEqual(0, mui([0, 0, 1, 1], [0, 1, 0, 1]))
        self.assertAlmostEqual(0, mui([0, 0, 1, 1], [0, 1, 1, 0]))
        self.assertAlmostEqual(0.3112781, mui([0, 0, 1, 1], [0, 1, 1, 1]))
        self.assertAlmostEqual(0.3112781, mui([0, 0, 1, 1], [1, 0, 0, 0]))
        self.assertAlmostEqual(0, mui([0, 0, 1, 1], [1, 0, 0, 1]))
        self.assertAlmostEqual(0, mui([0, 0, 1, 1], [1, 0, 1, 0]))
        self.assertAlmostEqual(1, mui([0, 0, 1, 1], [1, 1, 0, 0]))
        self.assertAlmostEqual(0.3112781, mui([0, 0, 1, 1], [1, 1, 0, 1]))
        self.assertAlmostEqual(0.3112781, mui([0, 0, 1, 1], [1, 1, 1, 0]))
        self.assertAlmostEqual(0, mui([0, 0, 1, 1], [1, 1, 1, 1]))

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main)