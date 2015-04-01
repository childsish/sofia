import unittest

from lhc.misc import cfgparse


class TestConfigParser(unittest.TestCase):
    def test_loadInt(self):
        cfg = cfgparse.loads('{"A": 1}')
        self.assertIn('A', cfg)
        self.assertEquals(1, cfg.A)

    def test_loadDictionary(self):
        cfg = cfgparse.loads('{"A": {"B": 1}}')
        self.assertIn('A', cfg)
        self.assertIn('B', cfg.A)
        self.assertEquals(1, cfg.A.B)

if __name__ == "__main__":
    unittest.main()
