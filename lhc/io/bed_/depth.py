import argparse
import itertools
import multiprocessing
import sys

from collections import Counter
from lhc.argparse import OpenWritableFile
from lhc.interval import Interval
from lhc.io.bed_.iterator import BedLineIterator
from lhc.io.bed_.set_ import BedSet
from lhc.io.sam_.iterator import SamLineIterator


def depth(args):
    in_fhndl = SamLineIterator(args.input)

    initargs = [args.bed]
    if args.processes == 1:
        init_worker(*initargs)
        it = itertools.imap(get_interval, in_fhndl)
    else:
        pool = multiprocessing.Pool(args.processes, initializer=init_worker, initargs=initargs)
        it = pool.imap(get_interval, in_fhndl, args.simultaneous_entries)

    depth = Counter(it)
    
    args.output.write('amplicon\tdepth\n')
    for interval in BedLineIterator(args.bed):
        args.output.write('{}\t{}\n'.format(interval.name, depth[interval.name]))

    sys.stderr.write('{} reads have no overlapping intervals'.format(depth[None]))

interval_set = None


def init_worker(bed_name):
    global interval_set
    interval_set = BedSet(BedLineIterator(bed_name))


def get_interval(read):
    read_interval = Interval(read.pos, read.pos + len(read.seq))
    try:
        matches = interval_set.get_overlapping_intervals(read.rname, read_interval.start, read_interval.stop)
        matches.sort(key=lambda x: len(read_interval.intersect(x)))
        match = matches[-1]
    except KeyError:
        return None
    except IndexError:
        return None
    return match


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    import sys

    add_arg = parser.add_argument
    add_arg('bed')
    add_arg('-i', '--input', default=sys.stdin)
    add_arg('-o', '--output', action=OpenWritableFile, default=sys.stdout,
            help='output destination (default: stdout)')
    add_arg('-p', '--processes', default=None, type=int,
            help='number of parallel processes')
    add_arg('-s', '--simultaneous-entries', default=1000000, type=int,
            help='number of entries to submit to each worker')
    parser.set_defaults(func=depth)
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())
