import unittest
import os
import numpy as np

from collections import OrderedDict
from tempfile import mkstemp
from lhc.binf.genomic_coordinate import Position, Interval
from lhc.binf.collection.marker_set import MarkerSet, Reference

class Test(unittest.TestCase):
    def setUp(self):
        fhndl, self.fname = mkstemp()
        os.close(fhndl)
    
    def testCreate(self):
        mrks = 'ACGATCAGGCT'
        ref = Reference(ref=np.vstack([list(mrks), list(mrks)]).T,
            poss=OrderedDict([
                ('Chr1', [5, 10, 15, 20, 25]),
                ('Chr2', [4, 6, 8, 10, 12, 14])
            ]))
        mrk_set = MarkerSet(self.fname, ref)
        
        self.assertIn('pos', mrk_set.data.dimensions)
        self.assertEquals(len(mrk_set.data.dimensions['pos']), 11)
        self.assertIn('ploidy', mrk_set.data.dimensions)
        self.assertIn('gen', mrk_set.data.dimensions)
        
        self.assertIn('chms', mrk_set.data.variables)
        self.assertEquals(mrk_set.data.variables['chms'][:].tolist(),
            [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1])
        self.assertIn('poss', mrk_set.data.variables)
        self.assertEquals(mrk_set.data.variables['poss'][:].tolist(),
            [5, 10, 15, 20, 25, 4, 6, 8, 10, 12, 14])
        self.assertIn('ref', mrk_set.data.variables)
        self.assertEquals(mrk_set.data.variables['ref'][:].tolist(),
            np.vstack([list(mrks), list(mrks)]).T.tolist())
        self.assertIn('snps', mrk_set.data.variables)
        
        self.assertIn('idxs', mrk_set.data.groups)
        self.assertIn('Chr1', mrk_set.data.groups['idxs'].variables)
        self.assertEquals(
            mrk_set.data.groups['idxs'].variables['Chr1'][:].tolist(),
            [0, 5])
        self.assertIn('Chr2', mrk_set.data.groups['idxs'].variables)
        self.assertEquals(
            mrk_set.data.groups['idxs'].variables['Chr2'][:].tolist(),
            [5, 11])
        
        self.assertIn('gens', mrk_set.data.groups)
        
        self.assertRaises(KeyError, mrk_set.getIndexAtPosition,
            Position('Chr1', 0))
    
    def testRegisterGenotype(self):
        mrks = 'ACGATCAGGCT'
        ref = Reference(ref=np.vstack([list(mrks), list(mrks)]).T,
            poss=OrderedDict([
                ('Chr1', [5, 10, 15, 20, 25]),
                ('Chr2', [4, 6, 8, 10, 12, 14])
            ]))
        mrk_set = MarkerSet(self.fname, ref)
        
        mrks = 'ACGACTGGGCT'
        mrk_set.registerGenotype('genotype_A',
            np.vstack([list(mrks), list(mrks)]).T)
        self.assertEquals(len(mrk_set.data.dimensions['gen']), 1)
        
        mrks = 'GTAATCAGGCT'
        mrk_set.registerGenotype('genotype_B',
            np.vstack([list(mrks), list(mrks)]).T)
        self.assertEquals(len(mrk_set.data.dimensions['gen']), 2)
        
        self.assertEquals(['A', 'G'],
            mrk_set.getMarkerAtPosition(Position('Chr1', 5))[:,0].tolist())
        self.assertEquals([list('ACGAC'), list('GTAAT')],
            mrk_set.getMarkersInInterval(Interval('Chr1', 0, 30))[:,:,0].tolist())
        self.assertEquals(['T', 'C'],
            mrk_set.getMarkerAtPosition(Position('Chr2', 4))[:,0].tolist())
        self.assertEquals([list('TGGGCT'), list('CAGGCT')],
            mrk_set.getMarkersInInterval(Interval('Chr2', 0, 30))[:,:,0].tolist())
        
        self.assertEquals(['genotype_A', 'genotype_B'],
            mrk_set.data.groups['gens'].variables.keys())
        self.assertEquals(''.join(mrk_set.getGenotype('genotype_A')[Position('Chr1', 5)]),
            'AA')
        self.assertEquals(''.join(mrk_set.getGenotype('genotype_B')[Position('Chr1', 5)]),
            'GG')

    def tearDown(self):
        os.remove(self.fname)

if __name__ == '__main__':
    unittest.main()
