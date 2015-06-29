__author__ = 'Liam Childs'

import argparse
import sys

from ..entity_parser import EntityParser


def check_format(input, format):
    parser = EntityParser()
    entity = parser.parse(format)

    for i, line in enumerate(input):
        parts = line.rstrip('\r\n').split('\t')
        try:
            entity(parts)
        except Exception, e:
            sys.stderr.write('Error parsing line number {}: {}\n'.format(i, e))
            sys.exit(1)
    sys.stdout.write('Check complete.\n')


# CLI


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    add_arg = parser.add_argument

    add_arg('input', nargs='?',
            help='input file (default: stdin)')
    add_arg('-f', '--format', default='s1',
            help='format to check (default: s1)')
    parser.set_defaults(func=init_check_format)

    return parser


def init_check_format(args):
    input = sys.stdin if args.input is None else open(args.input)
    check_format(input, args.format)
    input.close()


if __name__ == '__main__':
    sys.exit(main())
