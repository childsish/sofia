import argparse
import glob
import re

from collections import OrderedDict, defaultdict, Counter
from itertools import izip
from operator import add
from lhc.binf.identifier import Chromosome
from lhc.collections.sorted_dict import SortedDict
from lhc.argparse import OpenWritableFile
from iterator import VcfEntryIterator, Variant


class VcfMerger(object):
    
    CHR_REGX = re.compile('\d+$|X$|Y$|M$')
    
    def __init__(self, fnames, quality=0, depth=0, bams=[]):
        self.fnames = fnames
        self.quality = quality
        self.depth = depth
        self.iterators = [VcfEntryIterator(fname) for fname in fnames]
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


def merge(glob_fnames, quality=50.0, out=None, bams=[]):
    fnames = []
    for glob_fname in glob_fnames:
        fname = glob.glob(glob_fname)
        if len(fname) == 0:
            raise ValueError('{} does not match any existing files'.format(glob_fname))
        fnames.extend(fname)
    out = sys.stdout if out is None else open(out, 'w')
    merger = VcfMerger(fnames, quality, bams=bams)
    for key, values in merger.hdrs.iteritems():
        for value in values:
            out.write('{}={}\n'.format(key, value))
    out.write('#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\tFORMAT\t' + '\t'.join(merger.samples) + '\n')
    for entry in merger:
        format = sorted(key for key in entry.samples.itervalues().next().keys() if key != '.')
        out.write('{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\t{}\n'.format(
            entry.chr,
            entry.pos + 1,
            entry.id,
            entry.ref,
            entry.alt,
            entry.qual,
            entry.filter,
            entry.info,
            ':'.join(format),
            '\t'.join('.' if '.' in entry.samples[sample] else
                      ':'.join(entry.samples[sample][f] for f in format)
                      for sample in merger.samples)
        ))
    out.close()


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('inputs', nargs='+')
    add_arg('-b', '--bams', nargs='+',
            help='If provided, the read counts from the bam files with be included.')
    add_arg('-q', '--quality', type=float, default=0,
            help='Variants below the given quality are filtered.')
    add_arg('-o', '--output', default=sys.stdout, action=OpenWritableFile,
            help='The name of the merged vcf (default: stdout).')
    parser.set_defaults(func=lambda args: merge(args.inputs, args.quality, args.output, args.bams))
    return parser


if __name__ == '__main__':
    import sys
    sys.exit(main())