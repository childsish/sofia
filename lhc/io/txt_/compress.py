import argparse
import json

from tracker_factory import TrackerFactory
from index import FileIndex
from Bio.bgzf import BgzfWriter


class Partitioner(object):
    def __init__(self, fname, column_trackers):
        self.buffer = ''
        self.fhndl = open(fname)
        self.column_trackers = column_trackers

    def __iter__(self):
        return self

    def next(self):
        if self.buffer is None:
            raise StopIteration
        for line in self.fhndl:
            parts = line.rstrip('\r\n').split('\t')
            is_new_entry = [tracker.is_new_entry(parts) for tracker in self.column_trackers]
            if any(is_new_entry):
                key = tuple(tracker.get_key() for tracker in self.column_trackers)
                buffer = self.buffer

                self.buffer = line
                for tracker in self.column_trackers:
                    tracker.set_new_entry(parts)
                return key, buffer, any(is_new_entry[:-1])
            self.buffer += line
        buffer = self.buffer
        self.buffer = None
        return tuple(tracker.get_key() for tracker in self.column_trackers), buffer, False


def compress(args):
    if not args.extension.startswith('.'):
        args.extension = '.' + args.extension

    factory = TrackerFactory()
    column_trackers = [factory.make(column_type) for column_type in args.column_types]
    partitioner = Partitioner(args.input, column_trackers)
    index = FileIndex(len(args.column_types))
    out_fhndl = BgzfWriter(args.input + args.extension)
    key, buffer, break_block = partitioner.next()
    index[key] = out_fhndl.tell()
    for key, data, break_block in partitioner:
        if len(buffer) + len(data) > 65536 or break_block:
            out_fhndl.write(buffer)
            out_fhndl.flush()
            index[key] = out_fhndl.tell()
            buffer = ''
        buffer += data
    out_fhndl.close()

    out_fhndl = open(args.input + args.extension + '.lci', 'w')
    json.dump(index.__getstate__(), out_fhndl, indent=4, separators=(',', ': '))
    out_fhndl.close()


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input',
            help='input file name')
    add_arg('-c', '--column-types', nargs='+', default='1s',
            help='types for converting columns (default: 1s)')
    add_arg('-e', '--extension', default='.bgz',
            help='compressed file extension')
    parser.set_defaults(func=compress)
    return parser


if __name__ == '__main__':
    import sys
    sys.exit(main())
