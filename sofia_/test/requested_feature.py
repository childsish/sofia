import unittest

from ebias.requested_action import RequestedAction

class TestRequestedAction(unittest.TestCase):
    def test_equivalence(self):
        f1 = RequestedAction('f1', ['r1', 'r2'])
        f2 = RequestedAction('f1', ['r1', 'r2'])
        
        self.assertEquals(f1, f2)
        self.assertIn(f1, [f2])

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
