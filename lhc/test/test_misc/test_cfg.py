import unittest

from datetime import datetime
try:
    from lhc.misc import cfgparse
    import_failed = False
except ImportError:
    import_failed = True


class TestConfigParser(unittest.TestCase):
    def setUp(self):
        if import_failed:
            self.skipTest('Failed to import lhc.cfgparse')

    def test_loadBool(self):
        cfg = cfgparse.loads('A: true\nB: True\nC: TRUE')
        self.assertIn('A', cfg)
        self.assertIn('B', cfg)
        self.assertIn('C', cfg)
        self.assertTrue(cfg.A)
        self.assertTrue(cfg.B)
        self.assertTrue(cfg.C)

    def test_loadInt(self):
        cfg = cfgparse.loads('A: 1')
        self.assertIn('A', cfg)
        self.assertEquals(cfg.A, 1)

    def test_loadOct(self):
        cfg = cfgparse.loads('A: 0o1000')
        self.assertIn('A', cfg)
        self.assertEquals(cfg.A, 512)
        
    def test_loadHex(self):
        cfg = cfgparse.loads('A: 0x1000')
        self.assertIn('A', cfg)
        self.assertEquals(cfg.A, 4096)

    def test_loadDatetime1(self):
        cfg = cfgparse.loads('A: 2012-09-17')
        self.assertIn('A', cfg)
        self.assertEquals(cfg.A, datetime(2012, 9, 17))

    def test_loadDatetime2(self):
        cfg = cfgparse.loads('A: 2012-09-17 19:00:00')
        self.assertIn('A', cfg)
        self.assertEquals(cfg.A, datetime(2012, 9, 17, 19, 0, 0))

    def test_loadDictionary(self):
        cfg = cfgparse.loads('A: {B: 1}')
        self.assertIn('A', cfg)
        self.assertEquals(cfg.A, {'B': '1'})

    def test_loadSingleLineString(self):
        cfg = cfgparse.loads('A: 1')
        self.assertIn('A', cfg)
        self.assertEquals(cfg.A, 1)

if __name__ == "__main__":
    unittest.main()
