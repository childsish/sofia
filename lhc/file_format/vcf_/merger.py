import gzip

from collections import OrderedDict, defaultdict
from itertools import count, izip
from lhc.collection.sorted_dict import SortedDict
from parser import VcfParser, Variant
from operator import add

class VcfMerger(object):
    def __init__(self, fnames, quality=0):
        self.fnames = fnames
        self.quality = quality
        self.infiles = [gzip.open(fname) if fname.endswith('gz') else open(fname) for fname in fnames]
        self.hdrs, self.samples = self._mergeHeaders(list(VcfParser._parseHeaders(infile) for infile in self.infiles))

    def __iter__(self):
        n_samples = sum(map(len, self.samples))
        it = count()
        sample_names = []
        sample_idxs = []
        for samples in self.samples:
            sample_idxs.append([it.next() for sample in samples])
            sample_names.extend(samples)
        tops = [self._nextLine(idx) for idx in xrange(len(self.infiles))]
        sorted_tops = self._initSorting(tops)
        
        while len(sorted_tops) > 0:
            key, idxs = sorted_tops.popLowest()
            merged_alleles = [tops[idxs[0]][3]] + sorted(set(reduce(add, [tops[idx][4].split(',') for idx in idxs])))
            
            entry = tops[idxs[0]][:10]
            entry[4] = ','.join(merged_alleles[1:])
            entry[5] = '%.2f'%min(tops[idx][5] for idx in idxs)
            entry[7] = ''
            entry[8] = 'GT'
            
            samples = n_samples *  ['0/0']
            for idx in idxs:
                for i, sample in enumerate(tops[idx][9:]):
                    gt, sample = sample.split(':', 1)
                    a1, a2 = map(int, gt.split('/'))
                    alleles = [tops[idx][3]] + tops[idx][4].split(',')
                    sample = '/'.join(map(str, (merged_alleles.index(alleles[a1]), merged_alleles.index(alleles[a2]))))
                    samples[sample_idxs[idx][i]] = sample
            entry[9] = OrderedDict(izip(sample_names, samples))
            yield Variant(*entry)
            for idx in idxs:
                try:
                    tops[idx] = self._nextLine(idx)
                    self._updateSorting(sorted_tops, tops[idx], idx)
                except StopIteration:
                    pass
    
    def _nextLine(self, idx):
        while True:
            top = self.infiles[idx].next().strip().split('\t')
            top[1] = int(top[1]) - 1
            top[5] = float(top[5])
            if top[5] >= self.quality:
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
    
    def _mergeHeaders(self, hdrs):
        all_keys = defaultdict(list)
        for hdr in hdrs:
            for i, key in enumerate(hdr):
                all_keys[key].append(i)
        res = OrderedDict()
        for k, v in sorted(all_keys.iteritems(), key=lambda item: sum(item[1])):
            if k == '##SAMPLES':
                continue
            values = OrderedDict()
            for hdr in hdrs:
                values.update((value, None) for value in hdr[k])
            res[k] = list(values)
        samples = [hdr['##SAMPLES'] for hdr in hdrs]
        return res, samples
    
    def __del__(self):
        if hasattr(self, 'infiles'):
            for infile in self.infiles:
                if not infile.closed:
                    infile.close()
