__author__ = 'Liam Childs'

import argparse

from lhc.io.txt_ import IndexedSet, Set, Iterator


def fetch(set_, query):
    for entry in set_.fetch(query):
        yield entry


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    parser.add_argument('input', nargs='?')
    parser.add_argument('output', nargs='?')
    parser.add_argument('-q', '--query', nargs='+', default=[])
    parser.add_argument('-f', '--format', nargs='+', default=[])
    parser.set_defaults(func=fetch_init)
    return parser


def fetch_init(args):
    import os
    import sys

    if args.input is None:
        input = Set(Iterator(sys.stdin, args.format))
    elif os.exists(args.input + '.lci'):
        input = IndexedSet(args.input)
    else:
        input = Set(Iterator(args.input, args.format))
    output = sys.stdout if args.output is None else args.output
    fetch(input, output, args.query, args.format)

if __name__ == '__main__':
    import sys
    sys.exit(main())
