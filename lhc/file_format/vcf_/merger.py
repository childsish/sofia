import re

from collections import OrderedDict, defaultdict, Counter
from itertools import izip
from lhc.binf.identifier import Chromosome
from lhc.collection.sorted_dict import SortedDict
from iterator import VcfEntryIterator, Variant


class VcfMerger(object):
    
    CHR_REGX = re.compile('\d+$|X$|Y$|M$')
    
    def __init__(self, fnames, quality=0, depth=0, bams=[]):
        self.fnames = fnames
        self.quality = quality
        self.depth = depth
        self.iterators = map(VcfEntryIterator, fnames)
        hdrs = [it.hdrs for it in self.iterators]
        self.hdrs = self._merge_headers(hdrs)
        self.sample_names = self.hdrs['##SAMPLES']
        del self.hdrs['##SAMPLES']
        if len(bams) == 0:
            self.bams = []
            self.sample_to_bam = {}
        else:
            import pysam
            self.bams = []
            self.sample_to_bam = {}
            for bam_name in bams:
                bam = pysam.Samfile(bam_name)
                sample = bam.header['RG'][0]['SM'].strip()
                if sample in self.sample_names:
                    self.bams.append(bam)
                    self.sample_to_bam[sample] = bam
                else:
                    bam.close()

    def __iter__(self):
        """ Iterate through merged vcf lines.
    
        TODO: phased genotypes aren't handled
        """
        tops = [self._next_line(idx) for idx in xrange(len(self.iterators))]
        sorted_tops = self._init_sorting(tops)

        while len(sorted_tops) > 0:
            key, idxs = sorted_tops.pop_lowest()
            
            ref = sorted((tops[idx].ref for idx in idxs), key=lambda x: len(x))[-1]
            alt = set()
            sample_to_top = {}
            for idx in idxs:
                top = tops[idx]
                top_alt = [a + ref[len(top.ref):] for a in top.alt.split(',')]
                alt.update(top_alt)
                for sample in top.samples:
                    sample_to_top[sample] = (top, top_alt)
            alt = sorted(alt)
            
            format_ = {}
            samples = {}
            for sample_name in self.sample_names:
                if sample_name in sample_to_top:
                    top, top_alt = sample_to_top[sample_name]
                    sample_data = top.samples[sample_name]
                    if 'Q' not in format_:
                        format_['Q'] = ''
                    if 'GT' not in format_:
                        format_['GT'] = '0/0'
                    qual = sample_data['Q'] if 'Q' in sample_data else\
                        '' if top.qual == '.' else\
                        '{:.2f}'.format(top.qual)
                    samples[sample_name] = {'Q': qual}
                    samples[sample_name]['GT'] =\
                        self._get_gt(sample_data['GT'], top_alt, alt)
                    if 'GQ' in sample_data:
                        if 'GQ' not in format_:
                            format_['GQ'] = ''
                        samples[sample_name]['GQ'] = sample_data['GQ']
                    if 'RO' in sample_data:
                        if 'RO' not in format_:
                            format_['RO'] = '0'
                        if 'AO' not in format_:
                            format_['AO'] = ','.join('0' * len(alt))
                        samples[sample_name]['RO'] = sample_data['RO']
                        samples[sample_name]['AO'] = self._get_ao(sample_data['AO'], top.alt, alt)
                elif sample_name in self.sample_to_bam:
                    if 'GT' not in format_:
                        format_['GT'] = '0/0'
                    if 'RO' not in format_:
                        format_['RO'] = '0'
                    if 'AO' not in format_:
                        format_['AO'] = ','.join('0' * len(alt))
                    ro, ao = self._get_depth(sample_name, tops[idxs[0]].chr, tops[idxs[0]].pos, ref, alt)
                    samples[sample_name] = {'.': '.'} if ro is None else {'RO': ro, 'AO': ao}
                else:
                    samples[sample_name] = {'.': '.'}
            
            for sample in samples.itervalues():
                for fmt, default in format_.iteritems():
                    if fmt not in sample:
                        sample[fmt] = default

            yield Variant(tops[idxs[0]].chr,
                          tops[idxs[0]].pos,
                          tops[idxs[0]].id,
                          ref,
                          ','.join(alt),
                          min(tops[idx].qual for idx in idxs),
                          '.',
                          '.',
                          samples)

            for idx in idxs:
                try:
                    tops[idx] = self._next_line(idx)
                    self._update_sorting(sorted_tops, tops[idx], idx)
                except StopIteration:
                    pass
    
    def _next_line(self, idx):
        entry = self.iterators[idx].next()
        while entry.filter not in ['.', 'PASS'] or entry.qual < self.quality:
            entry = self.iterators[idx].next()
        return entry
    
    def _init_sorting(self, tops):
        sorted_tops = SortedDict()
        for idx, entry in enumerate(tops):
            self._update_sorting(sorted_tops, entry, idx)
        return sorted_tops
    
    def _update_sorting(self, sorted_tops, entry, idx):
        key = (Chromosome.get_identifier(entry.chr), entry.pos)
        sorted_tops.get(key, []).append(idx)
    
    def _merge_headers(self, hdrs):
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
    
    def _get_gt(self, gt, old_alt, new_alt):
        a1, a2 = map(int, gt.split('/'))
        if a1 != '0':
            a1 = str(new_alt.index(old_alt[a1 - 1]) + 1)
        if a2 != '0':
            a2 = str(new_alt.index(old_alt[a2 - 1]) + 1)
        return '{}/{}'.format(a1, a2)
    
    def _get_ao(self, ao, old_alt, new_alt):
        res = {k: v for k, v in izip(old_alt.split(','), ao.split(','))}
        return ','.join(res[a] if a in res else '0' for a in new_alt)
    
    def _get_depth(self, sample, chr, pos, ref, alt):
        bam = self.sample_to_bam[sample]
        ref_start = pos
        ref_stop = pos + len(ref)
        cnt = Counter()
        for read in bam.fetch(chr, ref_start, ref_stop):
            read_start, read_stop, truncated =\
                self._get_read_interval(read, ref_start, ref_stop)
            alt_seq = read.seq[read_start:read_stop]
            if truncated:  # assume reference
                alt_seq += ref[len(alt_seq):]
            cnt[alt_seq] += 1
        if cnt[ref] == 0 and all(cnt[a] == 0 for a in alt):
            return None, None
        return str(cnt[ref]), ','.join(str(cnt[a]) for a in alt)
    
    def _get_read_interval(self, read, ref_start, ref_stop):
        read_start = 0
        ref_pos = 0
        truncated = True
        read_pos = read.qstart
        for op, length in read.cigar:
            read_ext = [1, 1, 0, 1, 1, 1, 1, 1, 1][op] * length
            ref_ext = [1, 0, 1, 1, 1, 1, 1, 1, 1][op] * length
            if read.pos + ref_pos + ref_ext > ref_start and read_start == 0:
                read_start = read_pos + (ref_start - ref_pos - read.pos)
            if read.pos + ref_pos + ref_ext > ref_stop:
                truncated = False
                break
            read_pos += read_ext
            ref_pos += ref_ext
        read_stop = read_pos + (ref_stop - ref_pos - read.pos)
        return read_start, read_stop, truncated
