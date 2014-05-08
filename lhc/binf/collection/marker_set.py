import numpy as np

from bisect import bisect_left, bisect_right
from collections import Counter, namedtuple, OrderedDict
from netCDF4 import Dataset, default_fillvals
from lhc.binf.genomic_coordinate import Position, Interval

Reference = namedtuple('Reference', ['ref', 'poss'])

class MarkerSet(object):
    def __init__(self, fname):
        self.data = Dataset(fname)
        
        self.indices = self._initIndices(self.data)
        self.gen2idx, self.idx2gen = self._initGenotypes(self.data)
        self.muts = self._initMutations(self.data)
    
    def getGenotype(self, name):
        return Genotype(self, int(self.gen2idx[name]), name)
    
    def getMarkerAtPosition(self, pos):
        return self.getMarkerAtIndex(self.getIndexAtPosition(pos))

    def getIndexAtPosition(self, pos):
        chm_fr, chm_to = self.data.groups['idxs'].variables[pos.chr][:]
        poss_var = self.data.variables['poss']
        poss_idx = bisect_left(poss_var, pos.pos, chm_fr, chm_to)
        if poss_idx >= len(poss_var) or poss_var[poss_idx] != pos.pos:
            raise KeyError('Position does not exist')
        return poss_idx

    def getMarkerAtIndex(self, idx):
        return self.data.variables['snps'][:,idx,:]
    
    def getPositionAtIndex(self, idx):
        chm_idx = self.data.variables['chms'][idx]
        pos = self.data.variables['poss'][idx]
        return self.data.groups['idxs'].variables.keys()[chm_idx], pos
    
    def getMarkersInInterval(self, ivl):
        return self.getMarkersAtIndices(self.getIndicesInInterval(ivl))
        
    def getIndicesInInterval(self, ivl):
        chm_fr, chm_to = self.data.groups['idxs'].variables[ivl.chr][:]
        poss_var = self.data.variables['poss']
        pos_fr = bisect_left(poss_var, ivl.start, chm_fr, chm_to)
        pos_to = bisect_right(poss_var, ivl.stop, chm_fr, chm_to)
        return np.arange(pos_fr, pos_to, dtype='u4')
    
    def getMarkersAtIndices(self, idxs):
        return self.data.variables['snps'][:,idxs,:]
    
    def getPositionsAtIndices(self, idxs):
        return map(self.getPositionAtIndex, idxs)

    def processZygosity(self):
        """ Determine genotypes are homozygous (0/False) or heterozygous
            (1/True)
        """
        zygvar = self.data.variables['zygs']
        snpvar = self.data.variables['snps']
        for i in xrange(len(self.data.dimensions['gen'])):
            zyg_per_pos = snpvar[i,:,:] != np.matrix(snpvar[i,:,0]).T
            zygvar[i] = np.any(zyg_per_pos)
    
    def processAlleles(self):
        """ Initialise the minor allele variables (minor allele and the minor
            allele frequency)
        """
        malvar = self.data.variables['mal']
        mafvar = self.data.variables['maf']
        # Populate the variables
        snpvar = self.data.variables['snps']
        for i in xrange(len(self.data.dimensions['pos'])):
            cnt = Counter(snpvar[:,i,:].flatten())
            if np.ma.masked in cnt:
                del cnt[np.ma.masked]

            # Calculate per-position minor allele (frequency)
            if len(cnt) == 0:
                malvar[i] = default_fillvals['S1']
                mafvar[i] = 0
            else:
                malvar[i] = sorted(cnt.iterkeys(), key=lambda x:cnt[x])[0]
                mafvar[i] = min(cnt.itervalues()) / float(sum(cnt.itervalues()))

    def _initIndices(self, data):
        idx_grp = data.groups['indices']
        return OrderedDict((k, tuple(v[:]))\
            for k, v in idx_grp.variables.iteritems())
    
    def _initGenotypes(self, data):
        gen_grp = data.groups['genotypes']
        gen2idx = {k: v[0] for k, v in gen_grp.variables.iteritems()}
        idx2gen = [k for k, v in sorted(gen2idx.iteritems(), key=lambda x:x[1])]
        return gen2idx, idx2gen
    
    def _initMutations(self, data):
        muts = data.groups['mutations'].variables['muts'][:]
        np.ma.set_fill_value(muts, ' ')
        return [(ref.tostring().strip(), alt.tostring().strip())\
            for ref, alt in muts]

class Genotype(object):
    def __init__(self, mrk_set, idx, name):
        self.name = name
        self.mrk_set = mrk_set
        self.idx = idx
    
    def __getitem__(self, key):
        if isinstance(key, Position):
            idx = self.mrk_set.getIndexAtPosition(key)
        elif isinstance(key, Interval):
            idx = self.mrk_set.getIndicesInInterval(key)
        else:
            raise ValueError('Expected a Position or Interval from the genomic_coordinate package. Got %s.'%type(key))
        return self.mrk_set.data.variables['snps'][self.idx,idx]
