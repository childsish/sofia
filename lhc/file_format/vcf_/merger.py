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
        """ Iterate through merged vcf lines.
    
        TODO: phased genotypes aren't handled
        """
        tops = [self._nextLine(idx) for idx in xrange(len(self.iterators))]
        sorted_tops = self._initSorting(tops)
        
        while len(sorted_tops) > 0:
            key, idxs = sorted_tops.popLowest()
            
            refs = set(tops[idx].ref for idx in idxs)
            longest_ref = sorted(refs, key=lambda x:len(x))[-1]
            merged_alleles = set()
            for idx in idxs:
                top = list(tops[idx])
                ref = top[VcfIterator.REF]
                alts = [alt + longest_ref[len(ref):]\
                    for alt in top[VcfIterator.ALT].split(',')]
                merged_alleles.update(alts)
                top[VcfIterator.REF] = longest_ref
                top[VcfIterator.ALT] = alts
                tops[idx] = Variant(*top)
            merged_alleles = [longest_ref] + sorted(merged_alleles)
            entry = list(tops[idxs[0]])
            entry[VcfIterator.ALT] = ','.join(merged_alleles[1:])
            entry[VcfIterator.QUAL] = min(tops[idx].qual for idx in idxs)
            entry[VcfIterator.INFO] = '.'
            
            ao = ','.join((len(merged_alleles) - 1) * ['0'])
            samples = OrderedDict([(name, OrderedDict([('GT', '0/0'),
                                          ('GQ', '0'),
                                          ('RO', '0'),
                                          ('AO', ao),
                                          ('Q', '0')]))
                for name in self.sample_names])
            for idx in idxs:
                top = tops[idx]
                alleles = [longest_ref] + top.alt
                for sample_name, sample_data in top.samples.iteritems():
                    merged_counts = len(merged_alleles) * ['0']
                    counts = [sample_data['RO']] + sample_data['AO'].split(',')
                    for allele, count in izip(alleles, counts):
                        merged_counts[merged_alleles.index(allele)] = count
                    if sample_data['GT'] != '0/0':
                        try:
                            a1, a2 = map(int, sample_data['GT'].split('/'))
                        except Exception, e:
                            print self.iterators[idx].fname
                            raise e
                        sample_data['GT'] = '/'.join(map(str,\
                            (merged_alleles.index(alleles[a1]),\
                             merged_alleles.index(alleles[a2]))))
                    samples[sample_name]['GT'] = sample_data['GT']
                    samples[sample_name]['GQ'] = sample_data['GQ']
                    samples[sample_name]['RO'] = sample_data['RO']
                    samples[sample_name]['AO'] = ','.join(merged_counts[1:])
                    samples[sample_name]['Q'] = top.qual
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
        while entry.filter != 'PASS' and entry.qual < self.quality:
            entry = self.iterators[idx].next()
        return entry
    
    def _initSorting(self, tops):
        sorted_tops = SortedDict()
        for idx, entry in enumerate(tops):
            self._updateSorting(sorted_tops, entry, idx)
        return sorted_tops
    
    def _updateSorting(self, sorted_tops, entry, idx):
        key = (entry.chr, entry.pos)
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

