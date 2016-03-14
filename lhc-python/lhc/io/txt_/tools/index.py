import argparse
import gzip
import time

from ..entity_parser import EntityParser
from lhc.indices.tracked_index import TrackedIndex, save_index


def index(input, output, format='s1', header='#', delimiter='\t', factor=1):
    import sys

    entity_parser = EntityParser()
    entity_factory = entity_parser.parse(format)
    index = TrackedIndex(len(entity_factory.entities))

    t = time.time()
    i = 0
    while True:
        virtual_offset = input.tell()
        line = input.readline()
        i += 1
        if line == '':
            break
        elif line.startswith(header):
            continue
        entity = entity_factory(line.rstrip('\r\n').split(delimiter))
        index.add(entity, virtual_offset)
    sys.stderr.write('{} lines indexed in {} seconds\n'.format(i, time.time() - t))
    save_index(output, index)


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input',
            help='compressed file (using blocked gzip) to index')
    add_arg('-f', '--format', default='s1',
            help='format of the compressed file (default: s1)')
    add_arg('-a', '--header', default='#',
            help='character denoting a header line (default: #).')
    add_arg('-d', '--delimiter', default='\t',
            help='character delimiting the columns (default: \\t).')
    add_arg('-c', '--compression_factor', default=1,
            help='reduce the number of points to 1 / factor')
    add_arg('-z', '--zip', default=False, action='store_true',
            help='compress output using gzip (default: false)')
    parser.set_defaults(func=init_index)
    return parser


def init_index(args):
    raise NotImplementedError('removed until bgzf can be re-implemented')
    #input = bgzf.open(args.input, 'rb')
    output = gzip.open(args.input + '.lci', 'wb') if args.zip else open(args.input + '.lci', 'w')
    index(input, output, args.format, args.header, args.delimiter, args.compression_factor)
    input.close()
    output.close()

if __name__ == '__main__':
    import sys
    sys.exit(main())
