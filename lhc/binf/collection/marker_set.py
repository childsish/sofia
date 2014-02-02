import os
import codecs
import numpy as np

from bisect import bisect_left, bisect_right
from collections import Counter, namedtuple, OrderedDict
from netCDF4 import Dataset, default_fillvals
from lhc.binf.genomic_coordinate import Position, Interval

Reference = namedtuple('Reference', ['ref', 'poss'])

class MarkerSet(object):
    def __init__(self, fname, ref=None):
        self.fname = fname
        self.mode = 'r' if ref is None else 'w'
        self.closed = False
        self.data = Dataset(self.fname, self.mode)
        
        if self.mode == 'w':
            self.__initNewFile(ref)
        
        self.gen2idx = self.__initGenotypeMap()
    
    def __initNewFile(self, ref):
        npos = sum(map(len, ref.poss.itervalues()))
        
        self.data.createDimension('pos', npos)
        self.data.createDimension('ploidy', ref.ref.shape[1])
        self.data.createDimension('gen', None)
        
        chm_var = self.data.createVariable('chms', 'u1', ('pos',))
        pos_var = self.data.createVariable('poss', 'u4', ('pos',))
        self.data.createVariable('ref', 'S1', ('pos', 'ploidy'))[:] = ref.ref
        self.data.createVariable('snps', 'S1', ('gen', 'pos', 'ploidy'))

        idx_grp = self.data.createGroup('idxs')
        idx_grp.createDimension('rng', 2)
        fr = 0
        for chm_idx, (chm, chm_poss) in enumerate(ref.poss.iteritems()):
            to = fr + len(chm_poss)
            idx_grp.createVariable(chm, 'u4', ('rng',))[:] = [fr, to]
            chm_var[fr:to] = chm_idx
            pos_var[fr:to] = chm_poss
            fr = to
        
        gen_grp = self.data.createGroup('gens')
        gen_grp.createDimension('idx', 1)
    
    def __initGenotypeMap(self):
        idx2gen = {}
        for gen, idx in self.data.groups['gens'].variables.iteritems():
            idx = idx[0]
            if idx not in idx2gen:
                idx2gen[idx] = gen
        return OrderedDict([(gen, idx)\
            for idx, gen in sorted(idx2gen.iteritems())])
    
    def registerGenotype(self, name, markers=None, main_name=None):
        gens_grp = self.data.groups['gens']
        if main_name is not None and main_name not in gens_grp.variables:
            raise KeyError('Main name %s has not yet been registered'%main_name)
        
        if name in gens_grp.variables:
            idx = gens_grp.variables[name][0]
        else:
            idx = len(self.data.dimensions['gen']) if main_name is None\
                else gens_grp.variables[main_name][0]
            gens_grp.createVariable(name, 'u4', ('idx',))[0] = idx
            self.gen2idx[name] = idx
        
        if main_name is None and markers is None:
            markers = self.data.variables['ref'][:]
        if markers is not None:
            self.data.variables['snps'][idx,:,:] = markers
        
        return Genotype(self, idx)
    
    def getGenotype(self, name):
        return Genotype(self, self.gen2idx[name])
    
    def getMarkerAtPosition(self, pos):
        return self.getMarkerAtIndex(self.getIndexAtPosition(pos))

    def getIndexAtPosition(self, pos):
        chm_fr, chm_to = self.data.groups['idxs'].variables[pos.chr][:]
        poss_var = self.data.variables['poss']
        poss_idx = bisect_left(poss_var, pos.pos, chm_fr, chm_to)
        if poss_var[poss_idx] != pos.pos:
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

    def processNumerical(self):
        """ The numerical SNP matrix is represents the SNPs in numerical form,
            where each polymorphism is the sum of it's minor allele.
        """
        # Need the minor alleles to calculate
        if 'mal' not in self.data.variables:
            self.processAlleles()
        mal = self.data.variables['mal']

        # Initialise the numerical array
        if 'nsnps' in self.data.variables:
            nsnp = self.data.variables['nsnps']
        else:
            nsnp = self.data.createVariable('nsnps', 'f4', ('gens', 'poss'))
            nsnp.missing_value = default_fillvals['f4']

        # Calculate the numerical matrix
        csnp = self.data.variables['snps']
        nsnp[:] = np.sum(csnp[:] == mal[:][np.newaxis,:,np.newaxis], 2,
            dtype=np.dtype('f4'))

    def close(self):
        if hasattr(self, 'closed') and not self.closed and\
         hasattr(self, 'mode') and self.mode in 'wa':
            self.data.close()
            self.closed = True

class Genotype(object):
    def __init__(self, mrk_set, idx):
        self.mrk_set = mrk_set
        self.idx = idx
    
    def __getitem__(self, key):
        if isinstance(key, Position):
            idx = self.mrk_set.getIndexAtPosition(key)
        elif isinstance(key, Interval):
            idx = self.mrk_set.getIndicesInInterval(key)
        else:
            raise ValueError('Expected a Position or Interval from the genomic_coordinate package. Got %s.'%type(key))
        return self.mrk_set.data.variables['snps'][self.idx,idx,:]
