__author__ = 'Liam Childs'


"""
 * filter
 * pre-process
     1. sort
     2. compress
     3. index
 * fetch
 * join
"""

import argparse

from lhc.io.txt_ import IndexedSet, Iterator


def join(left, right, output):
    left_set = Iterator(left)
    right_set = IndexedSet(right)

    for left_entry in left_set:
        for right_entry in right_set.fetch(left_entry):
            output.write('{}\t{}\n'.format('\t'.join(left_entry), '\t'.join(right_entry)))


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    parser.set_defaults(func=join)
    return parser


def join_init(args):
    join(args.left, args.right, args.output)
