import argparse
import pysam

from lhc.file_format.bed import BedIterator, BedSet


def main():
    parser = get_parser()
    args = parser.parse_arguments()
    in_fhndl = pysam.AlignmentFile(args.input)
    out_fhndl = pysam.AlignmentFile(args.output, template=in_fhndl)
    intervals = BedSet(BedIterator(args.intervals))
    for entry in in_fhndl:
        matches = intervals.get_overlapping_intervals(entry.reference_id, entry.reference_start, entry.reference_end)
        if len(matches) == 0:
            continue
        match = sorted(matches, key=lambda x: entry.get_overlap(x))[-1][1]
        cigar = expand_cigar(entry.cigartuples)
        if entry.reference_start < match.start:
            for i in xrange(0, match.start - entry.reference_start):
                cigar[i] = 'S'
        if match.stop < entry.reference_end:
            for i in xrange(match.stop - entry.reference_end, -1):
                cigar[i] = 'S'
        entry.cigartuples = contract_cigar(cigar)
        out_fhndl.write(entry)


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
    return res


def get_parser():
    parser = argparse.ArgumentParser()


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input')
    add_arg('-o', '--output', default='-')
    add_arg('-i', '--intervals')


if __name__ == '__main__':
    import sys
    sys.exit(main)
