from collections import OrderedDict

from bisect import bisect_left, bisect_right
from lhc.binf.genomic_coordinate import Position

class PositionSet(object):
    def __init__(self, chrs, poss, chr_map=None):
        """A set of positions kept in a flat format
        
        :param list chrs: a list of the chromosome names for each position in
            poss.
        :param list poss: a list of all positions.
        :param dict chr_map: a dictionary defining where the chromosomes start
            and end in the variables chrs and poss.
        """
        assert len(chrs) == len(poss)
        self.chrs = chrs
        self.poss = poss
        self.chr_map = self._getChromosomeMap(chrs)\
            if chr_map is None else chr_map
    
    def __len__(self):
        return len(self.chrs)
    
    def getIndexAtPosition(self, pos):
        fr, to = self.chr_map[pos.chr]
        idx = bisect_left(self.poss, pos.pos, fr, to)
        if idx >= len(self.poss) or self.poss[idx] != pos.pos:
            raise KeyError('Position does not exist')
        return idx

    def getIndicesInInterval(self, ivl):
        chr_fr, chr_to = self.chr_map[ivl.chr]
        pos_fr = bisect_left(self.poss, ivl.start, chr_fr, chr_to)
        pos_to = bisect_right(self.poss, ivl.stop, chr_fr, chr_to)
        return np.arange(pos_fr, pos_to, dtype='u4')

    def getPositionAtIndex(self, idx):
        return Position(self.chrs[idx], self.poss[idx])

    def getPositionsAtIndices(self, idxs):
        return map(self.getPositionAtIndex, idxs)

    def _getChromosomeMap(self, chrs):
        chr_map = OrderedDict()
        fr = 0
        while fr < len(chrs):
            to = fr + 1
            while to < len(chrs) and chrs[fr] == chrs[to]:
                to += 1
            chr_map[chrs[fr]] = (fr, to)
            fr = to
        return chr_map

