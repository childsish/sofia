'''
Created on 05/08/2013

@author: Liam Childs
'''
import unittest
from lhc.interval import Interval as interval
from lhc.binf.collection.model_set import ModelSet


class Test(unittest.TestCase):

    def testAddSegment(self):
        mset = ModelSet(':memory:')
        model_id = mset.addModelSegment('chr1', interval(0, 10), 'gene', '+', None)
        qry = 'SELECT * FROM model WHERE id = ?'
        row = mset.conn.execute(qry, model_id)
        self.assertEquals((row.chr, row.ivl, row.type, row.strand, row.parent),
            ('chr1', interval(0, 10), 'gene', '+', None))

if __name__ == "__main__":
    unittest.main()