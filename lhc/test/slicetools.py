import unittest

from lhc import slicetools

class TestSliceTools(unittest.TestCase):
    def test_normalise(self):
        a = slice(5, 15)
        b = slice(-15, -5)
    
        self.assertEquals(slicetools.normalise(a), slice(5, 15))
        self.assertRaises(TypeError, slicetools.normalise, b)
        self.assertEquals(slicetools.normalise(b, 50), slice(35, 45))
    
    def test_overlaps(self):
        a = slice(0, 10)
        b = slice(6, 16)
        c = slice(12, 22)
    
        self.assertTrue(slicetools.overlaps(a, b))
        self.assertFalse(slicetools.overlaps(a, c))
        self.assertTrue(slicetools.overlaps(b, c))
    
    def test_getAbsPos(self):
        a = slice(5, 15)
        b = slice(-15, -5)
        
        self.assertEquals(slicetools.getAbsPos(a, 0), 5)
        self.assertEquals(slicetools.getAbsPos(a, 5), 10)
        self.assertEquals(slicetools.getAbsPos(a, 9), 14)
        self.assertRaises(IndexError, slicetools.getAbsPos, a, 10)
        self.assertEquals(slicetools.getAbsPos(b, 0, 50), 35)
        self.assertEquals(slicetools.getAbsPos(b, 5, 50), 40)
        self.assertEquals(slicetools.getAbsPos(b, 9, 50), 44)
        self.assertRaises(IndexError, slicetools.getAbsPos, b, 10, 50)
    
    def test_getRelPos(self):
        a = slice(5, 15)
        b = slice(-15, -5)
        
        self.assertEquals(slicetools.getRelPos(a, 5), 0)
        self.assertEquals(slicetools.getRelPos(a, 10), 5)
        self.assertEquals(slicetools.getRelPos(a, 14), 9)
        self.assertRaises(IndexError, slicetools.getRelPos, a, 15)
        self.assertEquals(slicetools.getRelPos(b, 35, 50), 0)
        self.assertEquals(slicetools.getRelPos(b, 40, 50), 5)
        self.assertEquals(slicetools.getRelPos(b, 44, 50), 9)
        self.assertRaises(IndexError, slicetools.getRelPos, b, 50, 50)
        

if __name__ == '__main__':
    unittest.main()
