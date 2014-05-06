import gzip

from itertools import count
from lhc.collection.sorted_dict import SortedDict
from lhc.file_format.vcf import VcfParser
from operator import add

class VcfMerger(object):
    def __init__(self, fnames, quality=50.0):
        self.fnames = fnames
        self.quality = quality
        self.infiles = [gzip.open(fname) if fname.endswith('gz') else open(fname) for fname in fnames]
        self.hdrs = [VcfParser._parseHeaders(infile) for infile in self.infiles]

    def __iter__(self):
        sample_namess = [hdr[-1][9:] for hdr in self.hdrs]
        n_samples = sum(map(len, sample_namess))
        it = count()
        sample_idxs = []
        for sample_names in sample_namess:
            sample_idxs.append([it.next() for i in xrange(len(sample_names))])
        tops = [self._nextLine(self.infiles, idx, self.quality) for idx in xrange(len(self.infiles))]
        sorted_tops = self._initSorting(tops)
        
        while len(sorted_tops) > 0:
            key, idxs = sorted_tops.popLowest()
            samples = n_samples *  ['0/0']
            for idx in idxs:
                for i, sample in enumerate(tops[idx][9:]):
                    samples[sample_idxs[idx][i]] = sample[:3]
            entry = tops[idxs[0]][:9]
            entry[4] = ','.join(set(reduce(add, [tops[idx][4].split(',') for idx in idxs])))
            entry[5] = '>%.2f'%min(tops[idx][5] for idx in idxs)
            entry[7] = ''
            entry[8] = 'GT'
            yield entry + samples
            for idx in idxs:
                try:
                    tops[idx] = self._nextLine(self.infiles, idx, self.quality)
                    self._updateSorting(sorted_tops, tops[idx], idx)
                except StopIteration:
                    pass
    
    def _nextLine(self, idx, quality=0):
        while True:
            top = self.infiles[idx].next().strip().split('\t')
            top[1] = int(top[1])
            top[5] = float(top[5])
            if top[5] >= quality:
                break
        return top
    
    def _initSorting(self, tops):
        sorted_tops = SortedDict()
        for idx, entry in enumerate(tops):
            self._updateSorting(sorted_tops, entry, idx)
        return sorted_tops
    
    def _updateSorting(self, sorted_tops, entry, idx):
        key = (entry[0], entry[1])
        sorted_tops.get(key, []).append(idx)
    
    def __del__(self):
        if hasattr(self, 'infiles'):
            for infile in self.infiles:
                if not infile.closed:
                    infile.close()
