'''
Created on 05/08/2013

@author: Liam Childs
'''
import os
import shutil
import unittest
import tempfile

from uuid import uuid4 as uuid
from lhc.binf.genomic_interval import interval
from lhc.binf.collection.model_set import ModelSet

class Test(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp()
    
    def getName(self):
        return os.path.join(self.tmpdir, str(uuid())[:8])

    def testAddSegment(self):
        mset = ModelSet(self.getName(), 'w')
        ivl = interval('chr1', 0, 10, '+')
        model_id = mset.addModelSegment(ivl, 'gene')
        mset.finaliseIntervals()
        
        qry = 'SELECT * FROM model WHERE id = ?'
        row = mset.conn.execute(qry, (model_id,)).fetchone()
        self.assertEquals(row, (model_id, ivl.chr, 0, 'gene', ivl.strand))
        
        mset_ivl = mset.ncl[0]
        self.assertEquals((mset_ivl.start, mset_ivl.stop), (ivl.start, ivl.stop))
    
    def testAddIdentifier(self):
        mset = ModelSet(self.getName(), 'w')
        ivl = interval('chr1', 0, 10, '+')
        model_id = mset.addModelSegment(ivl, 'gene')
        identifier_id = mset.addIdentifier(model_id, 'GENE_A')
        mset.finaliseIntervals()
        
        qry = 'SELECT * FROM identifier WHERE id = ?'
        row = mset.conn.execute(qry, (identifier_id,)).fetchone()
        self.assertEquals(row, (identifier_id, model_id, 'GENE_A', 'PRIMARY'))
    
    def testGetByIdentifier(self):
        mset = ModelSet(self.getName(), 'w')
        ivl = interval('chr1', 0, 10, '+')
        model_id = mset.addModelSegment(ivl, 'gene')
        mset.addIdentifier(model_id, 'GENE_A')
        mset.finaliseIntervals()
        
        res = mset['GENE_A']
        
        self.assertEquals((res.name, res.ivl, res.type), ('GENE_A', ivl, 'gene'))
    
    def testGetComplexModel(self):
        mset = ModelSet(self.getName(), 'w')
        ivl = interval('chr1', 0, 100, '+')
        parent_id = mset.addModelSegment(ivl, 'gene')
        mset.addIdentifier(parent_id, 'GENE_A')
        ivl = interval('chr1', 0, 100, '+')
        model_id = mset.addModelSegment(ivl, 'transcript', parent_id)
        mset.addIdentifier(model_id, 'GENE_A.0')
        ivl = interval('chr1', 0, 50, 100, '+')
        mset.addModelSegment(ivl, 'exon', model_id)
        ivl = interval('chr1', 60, 100, '+')
        mset.addModelSegment(ivl, 'exon', model_id)
        model_id = mset.addModelSegment(ivl, 'transcript', parent_id)
        mset.addIdentifier(model_id, 'GENE_A.1')
        ivl = interval('chr1', 0, 40, '+')
        mset.addModelSegment(ivl, 'exon', model_id)
        ivl = interval('chr1', 50, 100, '+')
        mset.addModelSegment(ivl, 'exon', model_id)
        mset.finaliseIntervals()

        res = mset['GENE_A']
        
        self.assertEquals(len(res.children), 2)
        self.assertEquals(set(child.name for child in res.children), set(('GENE_A.0', 'GENE_A.1')))
    
    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir)

if __name__ == "__main__":
    unittest.main()
