import gzip
import re

from collections import OrderedDict, defaultdict
from itertools import count, izip
from lhc.binf.identifier import Chromosome
from lhc.collection.sorted_dict import SortedDict
from parser import VcfParser, Variant
from operator import add

class VcfMerger(object):
    
    CHR_REGX = re.compile('\d+$|X$|Y$|M$')
    
    def __init__(self, fnames, quality=0):
        self.fnames = fnames
        self.quality = quality
        self.infiles = [gzip.open(fname) if fname.endswith('gz') else open(fname) for fname in fnames]
        hdrs = [VcfParser._parseHeaders(infile) for infile in self.infiles]
        self.hdrs = self._mergeHeaders(hdrs)
        self.sample_names, self.sample_idxs = self._mergeSamples(hdrs)

    def __iter__(self):
        tops = [self._nextLine(idx) for idx in xrange(len(self.infiles))]
        sorted_tops = self._initSorting(tops)
        
        while len(sorted_tops) > 0:
            key, idxs = sorted_tops.popLowest()
            merged_alleles = [tops[idxs[0]][3]] + sorted(set(reduce(add, [tops[idx][4].split(',') for idx in idxs])))
            
            entry = tops[idxs[0]][:9]
            entry[4] = ','.join(merged_alleles[1:])
            entry[5] = '%.2f'%min(tops[idx][5] for idx in idxs)
            entry[7] = ''
            
            samples = [OrderedDict([('GT', '0/0')])\
                for name in self.sample_names]
            for idx in idxs:
                for i, sample in enumerate(tops[idx][9:]):
                    gt, sample = sample.split(':', 1)
                    if gt == '0/0':
                        continue
                    a1, a2 = map(int, gt.split('/'))
                    alleles = [tops[idx][3]] + tops[idx][4].split(',')
                    sample = '/'.join(map(str, (merged_alleles.index(alleles[a1]), merged_alleles.index(alleles[a2]))))
                    samples[self.sample_idxs[idx][i]]['GT'] = sample
            entry[8] = OrderedDict(izip(self.sample_names, samples))
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
            top[0] = Chromosome.getIdentifier(top[0])
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
        return res
    
    def _mergeSamples(self, hdrs):
        sample_names = defaultdict(count().next)
        sample_idxs = [[sample_names[name] for name in hdr['##SAMPLES']] for hdr in hdrs] 
        return [k for k, v in sorted(sample_names.iteritems(), key=lambda x:x[1])], sample_idxs
    
    def __del__(self):
        if hasattr(self, 'infiles'):
            for infile in self.infiles:
                if not infile.closed:
                    infile.close()
