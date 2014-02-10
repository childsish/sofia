import unittest

from lhc.collection.nested_containment_list import NestedContainmentList as NCList

class Test(unittest.TestCase):
    def test_init(self):
        ivls = [slice(0, 10), slice(2, 30), slice(3, 20), slice(5, 7), slice(9, 15), slice(20, 25), slice(21, 22), slice(25, 31), slice(35, 39), slice(36, 39)]
        
        nclist = NCList(None)
        nclist._build(ivls)

if __name__ == "__main__":
    unittest.main()