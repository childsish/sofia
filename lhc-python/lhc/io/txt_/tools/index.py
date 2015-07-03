__author__ = 'Liam Childs'

import argparse
import gzip
import json
import time

from ..entity_parser import EntityParser
from ..index_parser import IndexParser
from lhc.indices.bgzf import PointIndex, IntervalIndex
from lhc.indices.bgzf.track import Track
from Bio import bgzf


class IndexEncoder(json.JSONEncoder):
    def default(self, o):
        if o in {PointIndex, IntervalIndex, Track}:
            return o.__name__[0]
        return super(IndexEncoder, self).default(o)


def index(input, output, format='s1'):
    entity_parser = EntityParser()
    index_parser = IndexParser()
    entity_factory = entity_parser.parse(format)
    index = index_parser.parse(entity_factory)

    t = time.time()
    i = 0
    while True:
        block_offset, inblock_offset = bgzf.split_virtual_offset(input.tell())
        line = input.readline()
        i += 1
        if line == '':
            break
        entity = entity_factory(line.rstrip('\r\n').split('\t'))
        index.add(entity, block_offset)
    index = index.compress()
    sys.stderr.write('{} lines indexed in {} seconds\n'.format(i, time.time() - t))

    json.dump(index.__getstate__(), output, cls=IndexEncoder)


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
    parser.set_defaults(func=init_index)
    return parser


def init_index(args):
    input = bgzf.open(args.input, 'rb')
    output = gzip.open(args.input + '.lci', 'wb')
    index(input, output, args.format)
    input.close()
    output.close()

if __name__ == '__main__':
    import sys
    sys.exit(main())
