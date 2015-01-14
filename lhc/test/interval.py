import unittest

from lhc.interval import Interval

class TestInterval(unittest.TestCase):
    
    def test_overlaps(self):
        a = Interval(0, 10)
        b = Interval(6, 16)
        c = Interval(12, 22)
        d = Interval(2, 8)
        e = Interval(10, 20)
    
        self.assertTrue(a.overlaps(b))
        self.assertTrue(b.overlaps(a))
        self.assertFalse(a.overlaps(c))
        self.assertFalse(c.overlaps(a))
        self.assertTrue(a.overlaps(d))
        self.assertTrue(d.overlaps(a))
        self.assertFalse(a.overlaps(e))
        self.assertFalse(e.overlaps(a))
    
    def test_contains(self):
        a = Interval(0, 10)
        b = Interval(6, 16)
        c = Interval(12, 22)
        d = Interval(2, 8)
        e = Interval(10, 20)
    
        self.assertFalse(a.contains(b))
        self.assertFalse(b.contains(a))
        self.assertFalse(a.contains(c))
        self.assertFalse(c.contains(a))
        self.assertTrue(a.contains(d))
        self.assertFalse(d.contains(a))
        self.assertFalse(a.contains(e))
        self.assertFalse(d.contains(e))
    
    def test_touches(self):
        a = Interval(0, 10)
        b = Interval(6, 16)
        c = Interval(12, 22)
        d = Interval(2, 8)
        e = Interval(10, 20)
    
        self.assertFalse(a.touches(b))
        self.assertFalse(b.touches(a))
        self.assertFalse(a.touches(c))
        self.assertFalse(c.touches(a))
        self.assertFalse(a.touches(d))
        self.assertFalse(d.touches(a))
        self.assertTrue(a.touches(e))
        self.assertTrue(e.touches(a))
    
    def test_getAbsPos(self):
        a = Interval(5, 15)
        
        self.assertEquals(a.get_abs_pos(0), 5)
        self.assertEquals(a.get_abs_pos(5), 10)
        self.assertEquals(a.get_abs_pos(9), 14)
        self.assertRaises(IndexError, a.get_abs_pos, 10)
    
    def test_getRelPos(self):
        a = Interval(5, 15)
        
        self.assertEquals(a.get_rel_pos(5), 0)
        self.assertEquals(a.get_rel_pos(10), 5)
        self.assertEquals(a.get_rel_pos(14), 9)
        self.assertRaises(IndexError, a.get_rel_pos, 15)
    
    def test_comparisons(self):
        a = Interval(0, 10)
        b = Interval(5, 10)
        c = Interval(5, 15)

        self.assertTrue(a == a)
        self.assertFalse(a == b)
        self.assertFalse(b == a)
        
        self.assertTrue(a < b)
        self.assertFalse(b < a)
        self.assertTrue(b < c)
        self.assertFalse(c < b)

if __name__ == '__main__':
    unittest.main()
