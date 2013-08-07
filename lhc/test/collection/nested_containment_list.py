'''
Created on 07/08/2013

@author: Liam Childs
'''
import unittest

from lhc.collection.nested_containment_list import NestedContainmentList as NCList

class Test(unittest.TestCase):


    def testGetInterval(self):
        ivls = [slice(0, 10), slice(0, 10), slice(1, 5), slice(6, 9), slice(0, 10), slice(1, 6), slice(7, 9), slice(20, 30),
            slice(20, 30), slice(21, 23), slice(24, 26), slice(27, 29), slice(20, 30), slice(21, 24), slice(27, 29)]
        ncl = NCList('/tmp/tmp.nc', 'w')
        ivl_map = ncl.insertIntervals(ivls)
        
        for i in xrange(len(ivls)):
            res = ncl[ivl_map[i]]
            self.assertEquals((ivls[i].start, ivls[i].stop), (res.start, res.stop))

    def testDiskless(self):
        ivls = [slice(0, 10), slice(0, 10), slice(1, 5), slice(6, 9), slice(0, 10), slice(1, 6), slice(7, 9), slice(20, 30),
            slice(20, 30), slice(21, 23), slice(24, 26), slice(27, 29), slice(20, 30), slice(21, 24), slice(27, 29)]
        ncl = NCList('.', 'w', diskless=True)
        ivl_map = ncl.insertIntervals(ivls)
        
        for i in xrange(len(ivls)):
            res = ncl[ivl_map[i]]
            self.assertEquals((ivls[i].start, ivls[i].stop), (res.start, res.stop))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()