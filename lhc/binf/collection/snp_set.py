import numpy as np

from bisect import bisect_left, bisect_right
from netCDF4 import Dataset


class SnpSet(object):
    """ A reader for the netCDF SNP set format

    Expected format:
    dimensions:
        pos: the number of positions
        ploidy: the ploidy of the organism
        gen: the number of genotypes
        gen_width: the length of the longest genotype name
    variables:
        u1 chrs(pos): the chromosome ids (names found in indices subgroup)
        u4 poss(pos): the position on the chromosome
        S1 ref(pos, ploidy): the reference sequence
        u4 snps(gen, pos, ploidy): the mutation ids (mutations found in mutations subgroup)
        S1 gens(gen, gen_width): the list of genotype names

    group: indices {
        dimensions:
            rng: always 2 (from and to)
        variables: each variable name is a chromosome name and the values are the range are the poss which are covered.
    }
    """

    CHROMOSOME_TYPE = 'u1'
    POSITION_TYPE = 'u4'
    CHARACTER_TYPE = 'S1'

    def __init__(self, fname, gens=None, ploidy=2):
        self.data = Dataset(fname)
        if len(self.data.variables) == 0:
            if gens is None:
                raise ValueError('A list of genotypes must be provided if the dataset if being created.')
            self._init_dataset(gens, ploidy)

    def add_position(self, chr, pos, snps, ref):
        data = self.data

        if chr not in data.groups['indices'].variables:
            prv_to = data.groups['indices'].variables.values()[-1][1]
            idx_var = data.groups['indices'].createVariable(chr, self.POSITION_TYPE, ('fr_to',))
            idx_var[:] = [prv_to, prv_to]
        idx_var = data.groups['indices'].variables[chr]
        idx_var[1] += 1

        chr_idx = len(data.groups['indices'].variables)
        n_idx = len(data.variables['poss'])
        data.variables['chrs'][n_idx] = chr_idx
        data.variables['poss'][n_idx] = pos
        data.variables['snps'][:,n_idx,:] = snps
        data.variables['ref'][n_idx] = ref

    def get_snp_at_position(self, chr, pos):
        return self.get_snp_at_index(self.get_index_at_position(chr, pos))

    def get_index_at_position(self, chr, pos):
        fr, to = self._get_chromosome_interval(chr)
        poss_var = self.data.variables['poss']
        poss_idx = bisect_left(poss_var, pos, fr, to)
        if poss_idx >= len(poss_var) or poss_var[poss_idx] != pos:
            raise KeyError('Position does not exist')
        return poss_idx

    def get_snp_at_index(self, idx):
        return self.data.variables['snps'][:,idx,:]

    def get_position_at_index(self, idx):
        chm_idx = self.data.variables['chms'][idx]
        pos = self.data.variables['poss'][idx]
        return self.data.groups['indices'].variables.keys()[chm_idx], pos

    def get_markers_in_interval(self, chr, start, stop):
        return self.get_markers_at_indices(self.get_indices_in_interval(chr, start, stop))

    def get_indices_in_interval(self, chr, start, stop):
        chm_fr, chm_to = self._get_chromosome_interval(chr)
        poss_var = self.data.variables['poss']
        pos_fr = bisect_left(poss_var, start, chm_fr, chm_to)
        pos_to = bisect_right(poss_var, stop, chm_fr, chm_to)
        return np.arange(pos_fr, pos_to, dtype=self.POSITION_TYPE)

    def get_markers_at_indices(self, idxs):
        return self.data.variables['muts'][:,idxs,:]

    def get_positions_at_indices(self, idxs):
        return map(self.get_position_at_index, idxs)

    def _init_dataset(self, gens, ploidy):
        data = self.data

        # Create dimensions
        data.createDimension('n_gen', len(gens))
        data.createDimension('n_pos', None)
        data.createDimension('n_ploidy', ploidy)
        data.createDimension('n_genchar', max(len(gen) for gen in gens))

        # Create variables
        data.createVariable('chrs', self.CHROMOSOME_TYPE, ('n_pos',))
        data.createVariable('poss', self.POSITION_TYPE, ('n_pos',))
        data.createVariable('ref', self.CHARACTER_TYPE, ('n_pos',))
        data.createVariable('snps', self.CHARACTER_TYPE, ('n_gen', 'n_pos', 'n_ploidy'))
        data.createVariable('gens', self.CHARACTER_TYPE, ('n_gen', 'n_genchar'))

        # Create chromosome index group
        indices = data.createGroup('indices')
        indices.createDimension('fr_to', 2)

    def _get_chromosome_interval(self, chr):
        return self.data.groups['indices'].variables[chr][:]
