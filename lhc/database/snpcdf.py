import os
import codecs
import json
import numpy as np

from netCDF4 import Dataset, default_fillvals
from functools import total_ordering
from collections import Counter
from lhc.enum import enum

Type = enum(['ID', 'MAIN', 'ALT', 'STOCK'])

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

class Alias(object):
    def __init__(self, name, typ=None):
        self.name = name
        self.type = typ

class Genotype(object):
    def __init__(self, id_, idx):
        self.id = id_
        self.idx = idx
        self.data = None
        self.aliases = [Alias(id_, Type.ID)]
    
    def __getitem__(self, key):
        key = self._checkKey(key)
        return self.data[key]
    
    def __setitem__(self, key, value):
        key = self._checkKey(key)
        self.data[key] = value
    
    def _checkKey(self, key):
        if isinstance(key, (int, slice)):
            key = (self.idx, key)
        elif isinstance(key, tuple):
            if len(key) > 2:
                raise IndexError('too many indices')
            key = (self.idx, key[0], key[1])
        return key
    
    def addAlias(self, alias):
        n_main = sum(alias.type == Type.MAIN for alias in self.aliases)
        if alias.type == Type.ID:
            if self.id is not None:
                raise ValueError('A genotype can not have more than one id')
            self.id = alias.name
        elif alias.type == Type.MAIN and n_main > 0:
            raise ValueError('A genotype can not have more than one main alias')
        elif alias.type is None and n_main == 0:
            alias.type = Type.MAIN
        elif alias.type is None:
            alias.type = Type.ALT
        self.aliases.append(alias)
    
    def getAliasByType(self, typ):
        res = []
        for alias in self.aliases:
            if alias.type == typ:
                res.append(alias)
        return res
    
class GenotypeSet(object):
    def __init__(self, fname, mode='r'):
        self.fname = fname
        self.mode = mode
        self._createIdx2Gen()
        self._createGen2Idx()
        self.closed = False
    
    def __del__(self):
        self.close()
    
    def __getitem__(self, key):
        if isinstance(key, int):
            return self.idx2gen[key]
        elif isinstance(key, basestring):
            res = [self.idx2gen[idx] for idx in self.gen2idx[key]]
            if len(res) == 1 and res[0].id == key:
                return res[0]
            return res
        raise KeyError('Unexpected key type. Get %s, expected <str>.'%\
            (type(key)))
    
    def addGenotype(self, genotype):
        self.idx2gen[genotype.idx] = genotype
        for alias in genotype.aliases:
            self.gen2idx[alias.name] = genotype.idx
    
    def _createIdx2Gen(self):
        self.idx2gen = {}
        if self.mode == 'w' or self.mode == 'a' and\
         not os.path.exists(self.fname):
            return
        infile = codecs.open(self.fname, encoding='utf-8')
        genotypes = json.load(infile)
        infile.close()
        for genotype in genotypes:
            gen = Genotype()
            for alias in genotype['aliases']:
                gen.addAlias(Alias(alias['name'], alias['type']))
            self.idx2gen[genotype['idx']] = gen

    def _createGen2Idx(self):
        self.gen2idx = {}
        for idx, genotype in self.idx2gen.iteritems():
            for alias in genotype.aliases:
                self.gen2idx.setdefault(alias.name, []).append(idx)
    
    def close(self):
        def genotypeToJson(gen):
            return {'idx': gen.idx, 'aliases':\
                [aliasToJson(alias) for alias in gen.aliases]}
        
        def aliasToJson(alias):
            return {'name': alias.name, 'type': alias.type}
        
        if hasattr(self, 'closed') and not self.closed and\
         hasattr(self, 'mode') and self.mode in 'wa':
            outfile = codecs.open(self.fname, 'w', encoding='utf-8')
            json.dump([genotypeToJson(gen)\
                    for idx, gen in self.idx2gen.iteritems()],
                outfile, indent=4)
            outfile.close()
            self.closed = True

class NetCDFMarkerSet(object):
    def __init__(self, fname, mode='r'):
        self.fname = fname
        self.mode = mode
        self.closed = False
        self.data = Dataset(fname, mode)
        self.gens = GenotypeSet('%s.json'%fname, mode)
    
    def __del__(self):
        self.close()
    
    def __getitem__(self, key):
        gens = self.gens[key]
        if isinstance(gen, list):
            for gen in gens:
                gen.data = self.data.variables['snps']
        else:
            gens.data = self.data.variables['snps']
        return gens

    def registerPositions(self, poss):
        chmvar, posvar, rnggrp = self._initDimensionsAndVariables(poss)
        fr = 0
        for chm, chm_poss in sorted(poss.iteritems()):
            to = fr + len(chm_poss)
            rnggrp.createVariable(chm, 'u4', ('rng',))[:] = np.array((fr, to))
            chmvar[fr:to] = chm
            posvar[fr:to] = chm_poss
            fr = to

    def _initDimensionsAndVariables(self, poss):
        """ Initialise as many variables as possible.
            WARNING: For some reason, if these variables are created out-of-
            order, a HDF error will occur when trying to save the file. The
            zygosity variable must be created before the reference variable has
            values assigned to it.
        """
        npos = sum(len(chm_poss) for chm, chm_poss in poss.iteritems())
        self.data.createDimension('gens', None)
        self.data.createDimension('poss', npos)
        genvar = self.data.createVariable('gens', 'u4', ('gens',))
        chmvar = self.data.createVariable('chms', 'S1', ('poss',))
        posvar = self.data.createVariable('poss', 'u4', ('poss',))
        zygvar = self.data.createVariable('zygs', 'u1', ('gens',)) # u1
        zygvar.missing_value = default_fillvals['i1']
        malvar = self.data.createVariable('mal', 'S1', ('poss',))
        malvar.missing_value = default_fillvals['S1']
        mafvar = self.data.createVariable('maf', 'f4', ('poss',))
        mafvar.missing_value = default_fillvals['f4']
        grp = self.data.createGroup('chm_idxs')
        grp.createDimension('rng', 2)
        return chmvar, posvar, grp
        
    def registerReference(self, ref, ploidy):
        self.data.createDimension('ploidy', ref.shape[1])
        refvar = self.data.createVariable('ref', 'S1', ('poss', 'ploidy'))
        snpvar = self.data.createVariable('snps', 'S1',
            ('gens', 'poss', 'ploidy'))
        snpvar.missing_value = default_fillvals['S1']
        refvar[:] = ref
        self.data.ploidy_multiplier = ploidy / ref.shape[1]

    def registerGenotype(self, id_=None):
        refvar = self.data.variables['ref']
        snpvar = self.data.variables['snps']
        nxt = len(self.data.dimensions['gens'])
        snpvar[nxt] = refvar[:]
        id_ = str(nxt + 1) if id_ is None else id_
        gen = Genotype(id_, nxt)
        gen.data = self.data.variables['snps']
        self.gens.addGenotype(gen)
        return gen
    
    def getChromosomeRanges(self):
        grp = self.data.groups['chm_idxs']
        return dict((chm, grp.variables[chm]) for chm in grp.variables)
    
    def processZygosity(self):
        """ Determine genotypes are homozygous (0/False) or heterozygous
            (1/True)
        """
        zygvar = self.data.variables['zygs']
        snpvar = self.data.variables['snps']
        for i in xrange(len(self.data.dimensions['gens'])):
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
        for i in xrange(len(self.data.dimensions['poss'])):
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
        nsnp[:] = self.data.ploidy_multiplier * nsnp[:]

    def processMatrix(self, name, pipe, kwargs, dim, dim_sz=None):
        if dim not in self.data.dimensions:
            self.data.createDimension(dim, dim_sz)
        snps = self.data.variables['nsnps'][:]
        for fn, args in izip(pipe, kwargs):
            snps = fn(snps, **args)
        if name in self.data.variables:
            var = self.data.variables[name]
        else:
            var = self.data.createVariable(name, 'f4', ('gens', dim))
        var[:] = snps
     
    def close(self):
        if hasattr(self, 'closed') and not self.closed and\
         hasattr(self, 'mode') and self.mode in 'wa':
            self.data.close()
            self.gens.close()
            self.closed = True
