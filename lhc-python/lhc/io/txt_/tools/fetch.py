__author__ = 'Liam Childs'

import argparse

from ..indexed_set import IndexedSet


def fetch(input, query, format):
    query = [eval(f)(q) for f, q in zip(format, query)]
    set_ = IndexedSet(input)
    print ''.join(set_.fetch(*query))


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    parser.add_argument('input')
    parser.add_argument('-q', '--query', nargs='+', default=[])
    parser.add_argument('-f', '--format', nargs='+', default=[])
    parser.set_defaults(func=fetch_init)
    return parser


def fetch_init(args):
    fetch(args.input, args.query, args.format)

if __name__ == '__main__':
    import sys
    sys.exit(main())
