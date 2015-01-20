import os
import tempfile
import unittest

from lhc.indices.exact_key import ExactKeyIndex
from lhc.io import csv

class TestCsv(unittest.TestCase):
    def setUp(self):
        self.fhndl, self.fname = tempfile.mkstemp()
        self.fhndl = os.fdopen(self.fhndl, 'w')
        self.fhndl.write('chr\tpos\tid\tdesc\n' +\
            '1\t100\trs839\tNever\n' +\
            '1\t200\trs581\twant\n' +\
            '2\t100\trs730\tto\n')
        self.fhndl.close()
    
    def test_convertColumnMap(self):
        it = iter(csv.CsvIterator(self.fname, column_map=[{'index': 0, 'name': 'chr'}, {'index': 1, 'name': 'pos', 'transform': 'int(pos) - 1'}, {'index': 3, 'name': 'desc'}]))
        
        line1 = it.next()
        line2 = it.next()
        line3 = it.next()
        
        self.assertEquals(line1.chr, '1')
        self.assertEquals(line1.pos, 99)
        self.assertEquals(line1.desc, 'Never')
        self.assertEquals(line2.chr, '1')
        self.assertEquals(line2.pos, 199)
        self.assertEquals(line2.desc, 'want')
        self.assertEquals(line3.chr, '2')
        self.assertEquals(line3.pos, 99)
        self.assertEquals(line3.desc, 'to')
    
    def test_getItem(self):
        csv.CsvSet.registerIndexType(ExactKeyIndex)
        it = csv.CsvIterator(self.fname, column_map=[{'index': 0, 'name': 'chr'}, {'index': 1, 'name': 'pos', 'transform': 'int(pos) - 1'}, {'index': 3, 'name': 'desc'}])
        csv_set = csv.CsvSet(it, [{'name': 'pos_index', 'column_map': [{'name': 'chr', 'index': 'ExactKeyIndex'}, {'name': 'pos', 'index': 'ExactKeyIndex'}], 'required_attributes': []}])
        
        self.assertEquals(csv_set[('1', 99)].chr, '1')
        self.assertEquals(csv_set[('1', 99)].pos, 99)
        self.assertEquals(csv_set[('1', 99)].desc, 'Never')
    
    def tearDown(self):
        os.remove(self.fname)

if __name__ == '__main__':
    import sys
    sys.exit(unittest.main())
