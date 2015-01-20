'''
Created on 23 Jul 2012

@author: childs
'''
import unittest
import random

from itertools import repeat
from lhc.parallel.mapreduce import MapReduce

def mymap(L):
    return [(x, 1) for x in L]

def myreduce(M):
    return (M[0], len(M[1]))

class Test(unittest.TestCase):
    def testWordCount(self):
        seq = ''.join('ACGT'[random.randint(0, 3)] for i in repeat(None, 2000000))
        words = [seq[i:i + 3] for i in xrange(len(seq) - 3)]
        mapreduce = MapReduce(mymap, myreduce, 1)
        
        print ''.join('%s\t%s\n'%ent for ent in dict(mapreduce(words)).items())

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
