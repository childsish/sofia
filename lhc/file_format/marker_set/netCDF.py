import os
import numpy as np

from netCDF4 import Dataset, default_fillvals
from functools import total_ordering

@total_ordering
class Position(object):
    def __init__(self, chm, pos=None):
        self.chm = chm
        self.pos = pos
    
    def __str__(self):
        return 'Chr%s:%d'%(self.chm, self.pos)
    
    def __eq__(self, other):
        return self.chm == other.chm and self.pos == other.pos
    
    def __lt__(self, other):
        return (self.chm < other.chm) or\
            (self.chm == other.chm) and (self.pos < other.pos)

class NetCDFMarkerSet(object):
    
    EXT = '.genotypes'
    
    def __init__(self, fname, mode='r'):
        self.fname = fname
        self.mode = mode
        self.closed = False
        self.idx2gen, self.gen2idx = self._loadGenotypes()
        self.root = Dataset(fname, mode)
    
    def _loadGenotypes(self):
        idx2gen = []
        gen2idx = {}
        fname = self._getGenotypeFileName()
        if self.mode != 'w' and os.path.exists(fname):
            infile = open(fname)
            idx2gen = infile.read().split()
            gen2idx = dict((gen, i) for i, gen in enumerate(self.idx2gen))
            infile.close()
        return idx2gen, gen2idx

    def __del__(self):
        self.close()

    def close(self):
        if hasattr(self, 'closed') and self.closed:
            return
        self.root.close()
        if self.mode == 'w':
            outfile = open(self._getGenotypeFileName(), 'w')
            outfile.write('\n'.join(self.idx2gen))
            outfile.close()

    def _getChromosomeIndices(self, chm):
        self.root.variable['chm_unq']
    
    def registerGenotypes(self, gens):
        self.root.createDimension('gens', len(gens))
        self.idx2gen.extend(gens)
        self.gen2idx.update(dict((gen, i) for i, gen in enumerate(gens)))
    
    def registerPositions(self, poss):
        self._registerChromosomeIndices(poss)
        self._registerPositions(poss)
    
    def _registerChromosomeIndices(self, poss):
        grp = self.root.createGroup('chm_idxs')
        grp.createDimension('rng', 2)
        chm = poss[0].chm
        fr = 0
        for to in xrange(len(poss)):
            if poss[to].chm != chm:
                rng = np.array((fr, to))
                grp.createVariable(chm, 'u4', ('rng',))[:] = rng
                chm = poss[to].chm
                fr = to
        rng = np.array((fr, len(poss)))
        grp.createVariable(chm, 'u4', ('rng',))[:] = rng

    def _registerPositions(self, poss):
        self.root.createDimension('poss', len(poss))
        chmvar = self.root.createVariable('chms', 'S1', ('poss',))
        chmvar[:] = [pos.chm for pos in poss]
        posvar = self.root.createVariable('poss', 'u4', ('poss',))
        posvar[:] = [pos.pos for pos in poss]
    
    def registerMarkers(self, snps, ploidy=2):
        self.root.createDimension('ploidy', ploidy)
        snpvar = self.root.createVariable('snps', 'S1',\
            ('gens', 'poss', 'ploidy'))
        snpvar.missing_value = default_fillvals['S1']
        for i in xrange(snps.shape[0]):
            snpvar[i,:,:] = snps[i,:,:]
    
    def _getGenotypeFileName(self):
        return '%s.%s'%(self.fname.split('.', 1)[0], NetCDFMarkerSet.EXT)
