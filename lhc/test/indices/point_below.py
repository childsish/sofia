import unittest

from lhc.indices.point_below import PointBelowIndex

class Test(unittest.TestCase):
    
    def test_getitem(self):
        index = PointBelowIndex()
        index[10] = [4, 5, 6]
        index[20] = [1, 2, 3]
        
        self.assertEquals(index[5], None)
        self.assertEquals(index[10], [4, 5, 6])
        self.assertEquals(index[11], [4, 5, 6])
        self.assertEquals(index[19], [4, 5, 6])
        self.assertEquals(index[20], [1, 2, 3])
        self.assertEquals(index[21], [1, 2, 3])

if __name__ == "__main__":
    unittest.main()
