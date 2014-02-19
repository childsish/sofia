'''
Created on 06/08/2013

@author: childsli
'''
import unittest

from lhc.file_format.gtf import iterGtf
from lhc.binf.genomic_coordinate import Interval

class Test(unittest.TestCase):

    def testIterGtf(self):
        fname = '/vol/home-vol3/wbi/childsli/data/annotation/hg19/gencode.v17.annotation.gtf'
        row = iterGtf(fname).next()
        self.assertEquals(row.ivl, interval('chr1', 11868, 14412, '+'))
        self.assertEquals(row.type, 'gene')
        self.assertEquals(row.attr, {'gene_status': 'KNOWN',
            'havana_gene': 'OTTHUMG00000000961.2', 'level': 2,
            'transcript_type': 'pseudogene', 'gene_id': 'ENSG00000223972.4',
            'transcript_id': 'ENSG00000223972.4', 'transcript_name': 'DDX11L1',
            'gene_type': 'pseudogene', 'transcript_status': 'KNOWN',
            'gene_name': 'DDX11L1'})

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()