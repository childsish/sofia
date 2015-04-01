import argparse
import json

from lhc.io.txt_.column_tracker import ColumnTracker, KeyColumnTracker
from lhc.io.txt_.index import FileIndex
from lhc.io.txt_.partitioner import Partitioner
from Bio.bgzf import BgzfWriter


class FastaEntryTracker(KeyColumnTracker):
    def convert(self, parts):
        line = parts[0]
        if line.startswith('>'):
            return line.split()[0][1:]
        return self.current_key


class FastaLineTracker(ColumnTracker):
    def convert(self, parts):
        return self.current_key + len(parts[0])

    def is_new_entry(self, parts):
        return True

    def set_new_entry(self, parts):
        self.current_key = 0 if parts[0].startswith('>') else self.convert(parts)


def compress(input, extension='.bgz'):
    if not extension.startswith('.'):
        extension = '.' + extension

    partitioner = Partitioner(input, [FastaEntryTracker([0], str), FastaLineTracker([0], str)])
    index = FileIndex(2)
    out_fhndl = BgzfWriter(input + extension)
    fpos = out_fhndl.tell()
    buffer, key, break_block = partitioner.next()
    for c_buffer, c_key, break_block in partitioner:
        if len(buffer) + len(c_buffer) >= 65536 or break_block:
            hdr_length = buffer.index('\n') + 1 if buffer.startswith('>') else 0
            index[key] = (fpos, len(buffer), hdr_length)
            out_fhndl.write(buffer)
            out_fhndl.flush()
            fpos = out_fhndl.tell()
            buffer = c_buffer
            key = c_key
        else:
            buffer += c_buffer
    hdr_length = buffer.index('\n') + 1 if buffer.startswith('>') else 0
    index[key] = (fpos, len(buffer), hdr_length)
    out_fhndl.write(buffer)
    out_fhndl.close()

    out_fhndl = open(input + extension + '.lci', 'w')
    json.dump(index.__getstate__(), out_fhndl, indent=4, separators=(',', ': '))
    out_fhndl.close()

    return input + extension


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input',
            help='input file name')
    add_arg('-e', '--extension', default='.bgz',
            help='compressed file extension')
    parser.set_defaults(func=lambda args: compress(args.input, args.extension))
    return parser


if __name__ == '__main__':
    import sys
    sys.exit(main())
