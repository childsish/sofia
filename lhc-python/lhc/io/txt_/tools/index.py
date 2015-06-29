__author__ = 'Liam Childs'

import argparse
import gzip
import json

from ..entity_parser import EntityParser
from ..index_parser import IndexParser
from Bio import bgzf


def index(input, output, format='s1'):
    entity_parser = EntityParser()
    index_parser = IndexParser()
    entity_factory = entity_parser.parse(format)
    index = index_parser.parse(entity_factory)
    while True:
        block_offset, inblock_offset = bgzf.split_virtual_offset(input.tell())
        line = input.readline()
        if line == '':
            break
        entity = entity_factory(line.rstrip('\r\n').split('\t'))
        index.add(entity, block_offset)
    json.dump(output, index.__getstate__())


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
    #output = gzip.open(args.input + '.lci', 'wb')
    output = open(args.input + '.lci', 'w')
    index(input, output, args.format)
    input.close()
    output.close()

if __name__ == '__main__':
    import sys
    sys.exit(main())
