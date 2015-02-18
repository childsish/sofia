import argparse
import json

from tracker_factory import TrackerFactory
from index import FileIndex
from partitioner import Partitioner
from Bio.bgzf import BgzfWriter


def compress(input, column_types='1s', extension='.bgz'):
    if not extension.startswith('.'):
        extension = '.' + extension

    factory = TrackerFactory()
    column_trackers = [factory.make(column_type) for column_type in column_types]
    partitioner = Partitioner(input, column_trackers)
    index = FileIndex(len(column_types))
    out_fhndl = BgzfWriter(input + extension)
    fpos = out_fhndl.tell()
    buffer, key, break_block = partitioner.next()
    for c_buffer, c_key, break_block in partitioner:
        if len(buffer) + len(c_buffer) >= 65536 or break_block:
            index[key] = (fpos, len(buffer))
            out_fhndl.write(buffer)
            out_fhndl.flush()
            fpos = out_fhndl.tell()
            key = c_key
            buffer = c_buffer
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
