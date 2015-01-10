import argparse
import pysam
import sys

from lhc.file_format.bed import BedEntryIterator, BedSet


def clip(args):
    in_fhndl = pysam.AlignmentFile(args.input)
    out_fhndl = pysam.AlignmentFile(args.output, 'wb', template=in_fhndl)
    intervals = BedSet(BedEntryIterator(args.bed))
    for entry in in_fhndl:
        matches = intervals.get_overlapping_intervals(in_fhndl.getrname(entry.reference_id),
                                                      entry.reference_start, entry.reference_end)
        if len(matches) == 0:
            continue
        match = sorted(matches, key=lambda x: entry.get_overlap(x.start, x.stop))[-1]
        cigar = expand_cigar(entry.cigartuples)
        sys.stderr.write('{}\n'.format(entry.query_name))
        sys.stderr.write('{}\t{}\t{}\t{}\n'.format(in_fhndl.getrname(entry.reference_id),
                                                   entry.reference_start, entry.reference_end, entry.is_reverse))
        sys.stderr.write('{}\t{}\t{}\n'.format(match.chr, match.start, match.stop))
        if entry.reference_start < match.start:
            cigar = clip_read(cigar, match.start - entry.reference_start + 1, '5p', entry.is_reverse)
            entry.reference_start = match.start + 1
        if match.stop < entry.reference_end:
            cigar = clip_read(cigar, entry.reference_end - match.stop, '3p', entry.is_reverse)
        sys.stderr.write(str(entry.cigartuples))
        sys.stderr.write('\n')
        sys.stderr.write(str(contract_cigar(cigar)))
        sys.stderr.write('\n')
        sys.stderr.write('\n')
        entry.cigartuples = contract_cigar(cigar)
        out_fhndl.write(entry)


def clip_read(cigar, overlap, end='5p', is_reverse=False):
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


def hard_clip_5p(cigar, to):
    ref_pos = 0
    read_pos = 0
    while ref_pos < to:
        op = cigar[read_pos]
        cigar[read_pos] = 5
        ref_pos += [1, 1, 0, 1, 1, 1, 1, 1, 1][op]
        read_pos += 1
    return cigar


def hard_clip_3p(cigar, fr):
    ref_pos = fr
    read_pos = fr
    while ref_pos < 0:
        op = cigar[read_pos]
        cigar[read_pos] = 5
        ref_pos += [1, 1, 0, 1, 1, 1, 1, 1, 1][op]
        read_pos += 1
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
    add_arg('-i', '--input', default='-')
    add_arg('-o', '--output', default='-')
    add_arg('-b', '--bed')
    parser.set_defaults(func=clip)
    return parser


if __name__ == '__main__':
    import sys
    sys.exit(main())
