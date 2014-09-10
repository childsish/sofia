import unittest

from ebias.requested_feature import RequestedFeature

class TestRequestedFeature(unittest.TestCase):
    def test_equivalence(self):
        f1 = RequestedFeature('f1', ['r1', 'r2'])
        f2 = RequestedFeature('f1', ['r1', 'r2'])
        
        self.assertEquals(f1, f2)
        self.assertIn(f1, [f2])

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
