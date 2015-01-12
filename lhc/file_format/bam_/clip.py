import argparse
import pysam

from lhc.file_format.bed import BedEntryIterator, BedSet

IN_READ_OPERATIONS =frozenset((0, 1, 4, 7, 8))


def clip(args):
    in_fhndl = pysam.AlignmentFile(args.input)
    out_fhndl = pysam.AlignmentFile(args.output, 'wb', template=in_fhndl)
    intervals = BedSet(BedEntryIterator(args.bed))
    for read in in_fhndl:
        if read.reference_id == -1:
            continue
        try:
            matches = intervals.get_overlapping_intervals(in_fhndl.getrname(read.reference_id),
                                                          read.reference_start, read.reference_end)
        except KeyError, e:
            sys.stderr.write('Warning, {} not found\n'.format(str(e)))
            continue
        if len(matches) == 0:
            continue
        match = sorted(matches, key=lambda x: read.get_overlap(x.start, x.stop))[-1]
        out_fhndl.write(clip_read(read, match))



def clip_read(read, match):
    if read.reference_start < match.start:
        read.reference_start = match.start

    cigar = expand_cigar(read.cigartuples)
    match_length = match.stop - read.reference_start

    i = 0
    cnt = read.reference_start - match.start
    while i < len(cigar) and cnt < 0:
        cnt += cigar[i] in IN_READ_OPERATIONS #  MIS=X: match, insert, soft clip, equal, different
        cigar[i] = 4
        i += 1
    while i < len(cigar) and cnt < match_length:
        cnt += cigar[i] in IN_READ_OPERATIONS #  MIS=X: match, insert, soft clip, equal, different
        i += 1
    while i < len(cigar):
        cigar[i] = 4
        i += 1

    read.cigartuples = contract_cigar(cigar)
    return read


def _clip_read(cigar, overlap, end='5p', is_reverse=False):
    it = xrange(-overlap, 0) if end == '3p' else\
        xrange(0, overlap)
    #it = xrange(-overlap, 0) if (end == '5p' and is_reverse) or (end == '3p' and not is_reverse) else\
    #    xrange(0, overlap)
    cnt = 0
    i = 0 if end == '5p' else len(cigar) - overlap
    while i < len(cigar) and cnt < overlap:
        if cigar[i] in (0, 2):
            cnt += 1
        cigar[i] = 4
        i += 1
    return cigar


def expand_cigar(cigar):
    res = []
    for op, l in cigar:
        res.extend(l * [op])
    return res


def contract_cigar(cigar):
    l = 0
    prv_op = cigar[0]
    res = []
    for op in cigar:
        if op != prv_op:
            res.append((prv_op, l))
            prv_op = op
            l = 0
        l += 1
    res.append((prv_op, l))
    return res


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input', default='-',
            help='The input bam file.')
    add_arg('-o', '--output', default='-',
            help='The output bam file (default: stdout).')
    add_arg('-b', '--bed',
            help='The intervals to clip the reads to.')
    parser.set_defaults(func=clip)
    return parser


if __name__ == '__main__':
    import sys
    sys.exit(main())
