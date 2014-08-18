import gzip
import re

from collections import OrderedDict, defaultdict
from itertools import count, izip
from lhc.binf.identifier import Chromosome
from lhc.collection.sorted_dict import SortedDict
from iterator import VcfIterator, Variant
from operator import add

class VcfMerger(object):
    
    CHR_REGX = re.compile('\d+$|X$|Y$|M$')
    
    def __init__(self, fnames, quality=0, depth=0):
        self.fnames = fnames
        self.quality = quality
        self.depth = depth
        self.iterators = map(VcfIterator, fnames)
        hdrs = [it.hdrs for it in self.iterators]
        self.hdrs = self._mergeHeaders(hdrs)
        self.sample_names = self.hdrs['##SAMPLES']
        del self.hdrs['##SAMPLES']

    def __iter__(self):
        tops = [self._nextLine(idx) for idx in xrange(len(self.iterators))]
        sorted_tops = self._initSorting(tops)
        
        while len(sorted_tops) > 0:
            key, idxs = sorted_tops.popLowest()
            
            merged_alleles = [tops[idxs[0]][3]] + sorted(set(reduce(add, [tops[idx][4].split(',') for idx in idxs])))
            #merged_alleles = sorted(set([top[3] for top in tops])) + sorted(set(reduce(add, [tops[idx][4].split(',') for idx in idxs])))
            entry = list(tops[idxs[0]])
            entry[4] = ','.join(merged_alleles[1:])
            entry[5] = min(tops[idx][5] for idx in idxs)
            entry[7] = '.'
            
            samples = OrderedDict([(name, OrderedDict([('GT', '0/0'),
                                          ('GQ', '0'),
                                          ('RO', '0'),
                                          ('AO', '0')]))\
                for name in self.sample_names])
            for idx in idxs:
                top = tops[idx]
                for sample_name, sample_data in top.samples.iteritems():
                    if sample_data['GT'] != '0/0':
                        try:
                            a1, a2 = map(int, sample_data['GT'].split('/'))
                        except Exception, e:
                            print self.iterators[idx].fname
                            raise e
                        alleles = [top[3]] + top[4].split(',')
                        sample_data['GT'] = '/'.join(map(str, (merged_alleles.index(alleles[a1]), merged_alleles.index(alleles[a2]))))
                    samples[sample_name]['GT'] = sample_data['GT']
                    samples[sample_name]['GQ'] = sample_data['GQ']
                    samples[sample_name]['RO'] = sample_data['RO']
                    samples[sample_name]['AO'] = sample_data['AO']
            entry[8] = samples
            yield Variant(*entry)
            for idx in idxs:
                try:
                    tops[idx] = self._nextLine(idx)
                    self._updateSorting(sorted_tops, tops[idx], idx)
                except StopIteration:
                    pass
    
    def _nextLine(self, idx):
        entry = self.iterators[idx].next()
        while entry.filter != 'PASS' and entry.quality < self.quality:
            entry = self.iterators[idx].next()
        return entry
    
    def _initSorting(self, tops):
        sorted_tops = SortedDict()
        for idx, entry in enumerate(tops):
            self._updateSorting(sorted_tops, entry, idx)
        return sorted_tops
    
    def _updateSorting(self, sorted_tops, entry, idx):
        key = (entry[0], entry[1], entry[3])
        sorted_tops.get(key, []).append(idx)
    
    def _mergeHeaders(self, hdrs):
        all_keys = defaultdict(list)
        for hdr in hdrs:
            for i, key in enumerate(hdr):
                all_keys[key].append(i)
        res = OrderedDict()
        for k, v in sorted(all_keys.iteritems(), key=lambda item: sum(item[1])):
            values = OrderedDict()
            for hdr in hdrs:
                values.update((value, None) for value in hdr[k])
            res[k] = list(values)
        return res

