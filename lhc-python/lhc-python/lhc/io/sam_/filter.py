import argparse
import itertools
import multiprocessing

from functools import partial
from lhc.argparse import OpenReadableFile, OpenWritableFile
from lhc.io.bed_.iterator import BedLineIterator
from lhc.io.bed_.set_ import BedSet
from lhc.io.sam_.iterator import SamLineIterator


def filter(args):
    filters = []
    if args.length:
        filters.append(partial(filter_length, length=args.length))
    if args.quality:
        filters.append(partial(filter_quality, quality=args.quality))
    if args.regions:
        filters.append(partial(filter_regions, regions=BedSet(BedLineIterator(args.regions))))

    in_fhndl = SamLineIterator(args.input)
    entry_iterator, pool_iterator = itertools.tee(in_fhndl)
    if args.processes == 1:
        init_worker(filters)
        it = itertools.imap(apply_filters, pool_iterator)
    else:
        pool = multiprocessing.Pool(args.processes, initializer=init_worker, initargs=[filters])
        it = pool.imap(apply_filters, pool_iterator, args.simultaneous_entries)
    
    cnt = {'dropped': 0, 'total': 0}
    out_fhndl = args.output
    out_fhndl.write('\n'.join(in_fhndl.hdrs))
    for read, keep in itertools.izip(entry_iterator, it):
        if keep:
            out_fhndl.write(str(read))
            out_fhndl.write('\n')
        else:
            cnt['dropped'] += 1
        cnt['total'] += 1
    out_fhndl.close()
    
    import sys
    sys.stderr.write('filtered {dropped} / {total} reads\n'.format(**cnt))


filters = None


def init_worker(filters_):
    global filters
    filters = filters_


def apply_filters(read):
    return all(f(read) for f in filters)


def filter_length(read, length):
    return len(read.seq) >= length


def filter_quality(read, quality):
    return read.mapq >= quality


def filter_regions(read, regions):
    try:
        return len(regions.fetch(read.rname, read.pos, read.pos + len(read.seq))) > 0
    except KeyError:
        pass
    return False


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    import sys
    add_arg = parser.add_argument
    add_arg('-i', '--input', default=sys.stdin, action=OpenReadableFile,
            help='input bam file (default: stdin).')
    add_arg('-l', '--length', type=int,
            help='remove reads longer than length')
    add_arg('-o', '--output', default=sys.stdout, action=OpenWritableFile,
            help='output bam file (default: stdout).')
    add_arg('-p', '--processes', type=int,
            help='number of processes to use')
    add_arg('-q', '--quality', type=float,
            help='remove reads with mapping quality less than quality')
    add_arg('-s', '--simultaneous-entries', default=100000, type=int,
            help='the number of entries to process in each worker')
    add_arg('-r', '--regions',
            help='bed file of regions the reads must overlap')
    parser.set_defaults(func=filter)
    return parser


if __name__ == '__main__':
    import sys
    sys.exit(main())
