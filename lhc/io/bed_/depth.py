import argparse
import itertools
import multiprocessing

from collections import Counter
from pysam import AlignmentFile, TabixFile
from lhc.argparse import OpenWritableFile
from lhc.io.bed_.iterator import BedLineIterator


def depth(args):
    interval_set = TabixFile(args.bed)
    alignment_file = AlignmentFile(args.bam)
    read_iterator, pool_iterator = itertools.tee(alignment_file)
    if args.cpus == 1:
        init_worker(interval_set, alignment_file)
        it = itertools.imap(get_interval, pool_iterator)
    else:
        initargs = [interval_set, alignment_file]
        pool = multiprocessing.Pool(args.cpus, initializer=init_worker, initargs=initargs)
        it = pool.imap(get_interval, pool_iterator)
    cnt = Counter()
    for read, interval in itertools.izip(read_iterator, it):
        if interval is not None:
            cnt[interval.name] += 1
    args.output.write(str(cnt))

interval_set = None
alignment_file = None


def init_worker(interval_set_, alignment_file_):
    global interval_set
    global alignment_file
    interval_set = interval_set_
    alignment_file = alignment_file_


def get_interval(read):
    try:
        intervals = [BedLineIterator.parse_line(line) for line in
                     interval_set.fetch(alignment_file.getrname(read.reference_id),
                                        read.reference_start, read.reference_end)]
    except ValueError, e:
        sys.stderr.write(str(e))
    if len(intervals) == 0:
        return None
    overlaps = [read.get_overlap(interval.start, interval.stop) for interval in intervals]
    overlap, interval = sorted(itertools.izip(overlaps, intervals))[-1]
    return interval


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    import sys

    add_arg = parser.add_argument
    add_arg('bed')
    add_arg('bam')
    add_arg('-c', '--cpus', default=None, type=int)
    add_arg('-o', '--output', action=OpenWritableFile, default=sys.stdout,
            help='Where to put the output (default: stdout).')
    parser.set_defaults(func=depth)
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
