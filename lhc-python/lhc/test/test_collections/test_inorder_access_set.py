import unittest

from lhc.collections.inorder_access_set import InOrderAccessSet


class TestInOrderAccessSet(unittest.TestCase):
    def setUp(self):
        self.points = [0, 10, 20, 30, 40, 50]
        self.key_points = [(0, 0, 'q'), (10, 0, 'w'), (10, 10, 'e'), (20, 0, 'r'), (20, 10, 't'), (20, 20, 'y')]

    def test_getByInterval(self):
        set_ = InOrderAccessSet(iter(self.points))

        self.assertEquals(set_.fetch(0, 10), [0])
        self.assertEquals(set_.fetch(10, 21), [10, 20])
        self.assertEquals(set_.fetch(30, 51), [30, 40, 50])
        self.assertEquals(set_.fetch(50, 51), [50])

    def test_getByPoint(self):
        set_ = InOrderAccessSet(iter(self.points))

        self.assertEquals(set_.fetch(0), [0])
        self.assertEquals(set_.fetch(10), [10])
        self.assertEquals(set_.fetch(30), [30])
        self.assertEquals(set_.fetch(50), [50])

    def test_getByKeyInterval(self):
        set_ = InOrderAccessSet(iter(self.key_points), key=[lambda x: x[0], lambda x: x[1]])

        self.assertEquals(set_.fetch(0, 0, 1), [(0, 0, 'q')])
        self.assertEquals(set_.fetch(10, 0, 10), [(10, 0, 'w')])
        self.assertEquals(set_.fetch(20, 0, 20), [(20, 0, 'r'), (20, 10, 't')])
        self.assertEquals(set_.fetch(20, 10, 21), [(20, 10, 't'), (20, 20, 'y')])

if __name__ == '__main__':
    unittest.main()
