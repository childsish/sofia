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


def compress(input, column_types='1s', extension='.bgz'):
    if not extension.startswith('.'):
        extension = '.' + extension

    factory = TrackerFactory()
    column_trackers = [factory.make(column_type) for column_type in column_types]
    partitioner = Partitioner(input, column_trackers)
    index = FileIndex(len(column_types))
    out_fhndl = BgzfWriter(input + extension)
    fpos = out_fhndl.tell()
    key, buffer, break_block = partitioner.next()
    for c_key, c_buffer, c_break_block in partitioner:
        if len(buffer) + len(c_buffer) >= 65536 or break_block:
            index[key] = (fpos, len(buffer))
            out_fhndl.write(buffer)
            out_fhndl.flush()
            fpos = out_fhndl.tell()
            key = c_key
            buffer = c_buffer
            break_block = c_break_block
        else:
            buffer += c_buffer
    index[key] = (fpos, len(buffer))
    out_fhndl.write(buffer)
    out_fhndl.close()

    out_fhndl = open(input + extension + '.lci', 'w')
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
    parser.set_defaults(func=lambda args: compress(args.input, args.column_types, args.extension))
    return parser


if __name__ == '__main__':
    import sys
    sys.exit(main())
