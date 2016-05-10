import argparse
import re

from operator import eq, ne, gt, ge, lt, le


def main():
    parser = get_parser()
    args = parser.parse_args()
    args.func(args)


def get_parser():
    parser = argparse.ArgumentParser()
    define_parser(parser)
    return parser


def define_parser(parser):
    parser.add_argument('input')
    parser.add_argument('filters', nargs='+')
    parser.set_defaults(func=filter)


def filter(args):
    ops = {
        '==': (eq, str),
        '!=': (ne, str),
        '>': (gt, float),
        '>=': (ge, float),
        '<': (lt, float),
        '<=': (le, float)
    }
    op_regx = re.compile('^(?P<key>[\w:,]+)(?P<op>(==)|(!=)|(>)|(>=)|(<)|(<=))(?P<value>.*)$')
    
    infile = open(args.input)
    header_line = infile.readline()
    headers = header_line.strip().split('\t')
    filters = []
    for filter in args.filters:
        match = op_regx.match(filter)
        if match is None:
            raise ValueError('Invalid filter definition: {}'.format(filter))
        else:
            op, type = ops[match.group('op')]
            key = match.group('key')
            value = type(match.group('value'))
            filters.append((headers.index(key), type, value, op))
    sys.stdout.write(header_line)
    for line in infile:
        parts = line.strip().split('\t')
        keep = True
        for idx, type, value, op in filters:
            if not op(type(parts[idx]), value):
                keep = False
                break
        if keep:
            sys.stdout.write(line)

if __name__ == '__main__':
    import sys
    sys.exit(main())
