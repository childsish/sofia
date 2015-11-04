import re

from collections import OrderedDict, defaultdict, Counter
from itertools import izip
from operator import add
from lhc.binf.identifier import Chromosome
from lhc.collections.sorted_dict import SortedDict
from iterator import VcfEntryIterator, Variant


class VcfMerger(object):
    
    CHR_REGX = re.compile('\d+$|X$|Y$|M$')
    
    def __init__(self, iterators, bams=[]):
        self.iterators = [VcfEntryIterator(i) for i in iterators]
        hdrs = [it.hdrs for it in self.iterators]
        self.hdrs = self._merge_headers(hdrs)
        self.samples = reduce(add, [it.samples for it in self.iterators])
        if bams is None or len(bams) == 0:
            self.bams = []
            self.sample_to_bam = {}
        else:
            import pysam
            self.bams = []
            self.sample_to_bam = {}
            for bam_name in bams:
                bam = pysam.Samfile(bam_name)
                sample = bam.header['RG'][0]['SM'].strip()
                if sample in self.samples:
                    self.bams.append(bam)
                    self.sample_to_bam[sample] = bam
                else:
                    bam.close()

    def __iter__(self):
        """ Iterate through merged vcf_ lines.
    
        TODO: phased genotypes aren't handled
        """
        tops = [iterator.next() for iterator in self.iterators]
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
            for sample_name in self.samples:
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
                        self._get_gt(sample_data['GT'], top_alt, alt) if 'GT' in sample_data else\
                        './.'
                    if 'GQ' in sample_data:
                        if 'GQ' not in format_:
                            format_['GQ'] = ''
                        samples[sample_name]['GQ'] = sample_data['GQ']
                    if 'RO' in sample_data:
                        if 'RO' not in format_:
                            format_['RO'] = '0'
                        if 'AO' not in format_:
                            format_['AO'] = ','.join('0' * len(alt))
                        if 'AF' not in format_:
                            format_['AF'] = '0'
                        samples[sample_name]['RO'] = sample_data['RO']
                        samples[sample_name]['AO'] = self._get_ao(sample_data['AO'], top.alt, alt)
                        if samples[sample_name]['AO'] is None or samples[sample_name]['RO'] is None:
                            continue
                        ro = float(samples[sample_name]['RO'])
                        aos = [float(ao) for ao in samples[sample_name]['AO'].split(',')]
                        afs = [ao / (ro + ao) if ro + ao > 0 else 0 for ao in aos]
                        samples[sample_name]['AF'] = ','.join('{:.3f}'.format(af) for af in afs)
                elif sample_name in self.sample_to_bam:
                    if 'GT' not in format_:
                        format_['GT'] = '0/0'
                    if 'RO' not in format_:
                        format_['RO'] = '0'
                    if 'AO' not in format_:
                        format_['AO'] = ','.join('0' * len(alt))
                    if 'AF' not in format_:
                        format_['AF'] = '0'
                    ro, aos = self._get_depth(sample_name, tops[idxs[0]].chr, tops[idxs[0]].pos, ref, alt)
                    samples[sample_name] = {'.': '.'} if ro is None else {
                        'RO': ro,
                        'AO': aos,
                    }
                    if ro is None or aos is None:
                        continue
                    ro = float(ro)
                    aos = [float(ao) for ao in aos.split(',')]
                    afs = [ao / (ro + ao) if ro + ao > 0 else 0 for ao in aos]
                    samples[sample_name]['AF'] = ','.join('{:.3f}'.format(af) for af in afs)
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
                    tops[idx] = self.iterators[idx].next()
                    self._update_sorting(sorted_tops, tops[idx], idx)
                except StopIteration:
                    pass
    
    def _init_sorting(self, tops):
        sorted_tops = SortedDict()
        for idx, entry in enumerate(tops):
            self._update_sorting(sorted_tops, entry, idx)
        return sorted_tops
    
    def _update_sorting(self, sorted_tops, entry, idx):
        key = (Chromosome.get_identifier(entry.chr), entry.pos)
        if key not in sorted_tops:
            sorted_tops[key] = []
        sorted_tops[key].append(idx)
    
    def _merge_headers(self, hdrs):
        all_keys = defaultdict(list)
        for hdr in hdrs:
            for i, key in enumerate(hdr):
                all_keys[key].append(i)
        res = OrderedDict()
        for k, v in sorted(all_keys.iteritems(), key=lambda item: sum(item[1])):
            values = OrderedDict()
            for hdr in hdrs:
                if k in hdr:
                    values.update((value, None) for value in hdr[k])
            res[k] = list(values)
        return res
    
    def _get_gt(self, gt, old_alt, new_alt):
        try:
            a1, a2 = map(int, gt.split('/'))
        except ValueError:
            return './.'
        a1 = new_alt.index(old_alt[a1 - 1]) + 1 if 0 < a1 <= len(old_alt) else 0
        a2 = new_alt.index(old_alt[a2 - 1]) + 1 if 0 < a2 <= len(old_alt) else 0
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
