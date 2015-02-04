import argparse
import itertools
import multiprocessing
import re
import sys

from collections import Counter
from lhc.argparse import OpenWritableFile
from lhc.interval import Interval
from lhc.io.bed_.iterator import BedLineIterator
from lhc.io.bed_.set_ import BedSet
from lhc.io.sam_.iterator import SamLineIterator, SamLine


def clip(args):
    in_fhndl = SamLineIterator(args.input)

    initargs = [args.bed_file, args.five_prime_offset, args.three_prime_offset]
    if args.processes == 1:
        init_worker(*initargs)
        it = itertools.imap(clip_read, in_fhndl)
    else:
        pool = multiprocessing.Pool(args.processes, initializer=init_worker, initargs=initargs)
        it = pool.imap(clip_read, in_fhndl, args.simultaneous)
    
    msgs = Counter()
    out_fhndl = args.output
    out_fhndl.write('\n'.join(in_fhndl.hdrs))
    out_fhndl.write('\n')
    for read, msg in it:
        out_fhndl.write(str(read))
        out_fhndl.write('\n')
        msgs[msg] += 1
    
    sys.stderr.write('the following messages were encountered:\n')
    for msg, cnt in sorted(msgs.iteritems()):
        sys.stderr.write(' {} times: {}\n'.format(cnt, msg))


intervals = None
offset_5p = None
offset_3p = None
regx = re.compile('(\d+)([MIDNSHP=X])')


def init_worker(bed_fname, offset_5p_, offset_3p_):
    global intervals
    global offset_5p
    global offset_3p

    intervals = BedSet(BedLineIterator(bed_fname))
    offset_5p = offset_5p_
    offset_3p = offset_3p_


def clip_read(read):
    read_interval = Interval(read.pos, read.pos + len(read.seq))
    try:
        matches = intervals.get_overlapping_intervals(read.rname, read_interval.start, read_interval.stop)
        matches.sort(key=lambda x: len(read_interval.intersect(x)))
        match = matches[-1]
    except KeyError, e:
        return read, 'warning, reference sequence "{}" not found'.format(str(e))
    except IndexError:
        return read, 'warning, no overlapping intervals'
    match = Interval(match.start + offset_5p + 1, match.stop + offset_3p)
    
    cigar = expand_cigar(read.cigar)
    cnt_b4 = Counter(cigar)
    cigar_b4 = cigar[:]
    
    ref_pos = read.pos
    read_pos = cigar.index('M')
    while read_pos < len(cigar) and ref_pos < match.start:
        if cigar[read_pos] in 'MIS=X':
            cigar[read_pos] = 'S'
        ref_pos += cigar[read_pos] in 'MIS=X'
        read_pos += 1
    pos = ref_pos
    while read_pos < len(cigar) and ref_pos < match.stop:
        ref_pos += cigar[read_pos] in 'MIS=X'
        read_pos += 1
    while read_pos < len(cigar):
        if cigar[read_pos] in 'MIS=X':
            cigar[read_pos] = 'S'
        read_pos += 1
    
    parts = list(read)
    parts[3] = pos
    parts[5] = contract_cigar(cigar)
    return SamLine(*parts), 'clipped'


def expand_cigar(cigar):
    res = []
    for l, op in regx.findall(cigar):
        res.extend(int(l) * [op])
    return res


def contract_cigar(cigar):
    l = 0
    prv_op = cigar[0]
    res = []
    for op in cigar:
        if op != prv_op:
            res.append('{}{}'.format(l, prv_op))
            prv_op = op
            l = 0
        l += 1
    res.append('{}{}'.format(l, prv_op))
    return ''.join(res)


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    import sys
    add_arg = parser.add_argument
    add_arg('bed_file',
            help='intervals to clip the reads to')
    add_arg('-5', '--five-prime-offset', default=0, type=int,
            help='where to trim relative to five prime position of intervals')
    add_arg('-3', '--three-prime-offset', default=0, type=int,
            help='where to trim relative to three prime position of intervals')
    add_arg('-i', '--input', default=sys.stdin,
            help='input bam file (default: stdin)')
    add_arg('-o', '--output', default=sys.stdout, action=OpenWritableFile,
            help='output bam file (default: stdout)')
    add_arg('-p', '--processes', type=int,
            help='use given number of processes')
    add_arg('-s', '--simultaneous', type=int, default=10000,
            help='number of simultaneous entries in each worker')
    parser.set_defaults(func=clip)
    return parser


if __name__ == '__main__':
    import sys
    sys.exit(main())
