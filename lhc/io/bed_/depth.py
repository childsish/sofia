import argparse
import itertools
import multiprocessing
import sys

from collections import Counter
from pysam import AlignmentFile
from lhc.argparse import OpenWritableFile
from lhc.io.bed_.iterator import BedLineIterator
from lhc.io.bed_.set_ import BedSet


def depth(args):
    alignment_file = AlignmentFile(args.bam)
    read_iterator, pool_iterator = itertools.tee(alignment_file)
    if args.cpus == 1:
        init_worker(args.bed, args.bam)
        it = itertools.imap(get_interval, pool_iterator)
    else:
        initargs = [args.bed, args.bam]
        pool = multiprocessing.Pool(args.cpus, initializer=init_worker, initargs=initargs)
        it = pool.imap(get_interval, pool_iterator, args.simultaneous_entries)
    cnt = Counter()
    for read, interval in itertools.izip(read_iterator, it):
        if interval is not None:
            cnt[interval.name] += 1
    for k, v in sorted(cnt.iteritems(), key=lambda x: x[1]):
        args.output.write('{}\t{}\n'.format(k, v))

interval_set = None
alignment_file = None


def init_worker(bed_name, bam_name):
    global interval_set
    global alignment_file
    interval_set = BedSet(BedLineIterator(bed_name))
    alignment_file = AlignmentFile(bam_name)


def get_interval(read):
    try:
        intervals = interval_set.get_overlapping_intervals(alignment_file.getrname(read.reference_id),
                                                           read.reference_start, read.reference_end)
    except KeyError, e:
        intervals = []
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
    add_arg('-s', '--simultaneous-entries', default=1000000, type=int,
            help='The number of entries to submit to each worker.')
    parser.set_defaults(func=depth)
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
