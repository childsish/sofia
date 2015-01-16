import argparse
import pysam

from lhc.file_format.bed import BedEntryIterator, BedSet
import sys

IN_READ_OPERATIONS = (1, 0, 1, 0, 0, 0, 0, 0, 0)  # match, delete


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
    cigar = expand_cigar(read.cigartuples)
    match_length = match.stop - match.start - 1
    cnt = read.reference_start - match.start - 1
    if cnt < 0:
        read.reference_start -= cnt
    i = 0
    while i < len(cigar) and cnt < 0:
        cnt += IN_READ_OPERATIONS[cigar[i]]
        cigar[i] = 4
        i += 1
    while i < len(cigar) and cnt < match_length:
        cnt += IN_READ_OPERATIONS[cigar[i]]
        i += 1
    while i < len(cigar):
        cigar[i] = 4
        i += 1
    read.cigartuples = contract_cigar(cigar)
    return read


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
    add_arg('-i', '--input', default='-',
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
