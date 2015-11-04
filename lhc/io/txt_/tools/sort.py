import argparse
import time

from ..iterator import Iterator
from ..format_parser import FormatParser
from itertools import chain
from lhc.tools.sorter import Sorter


def sort(input, output, format='s1', max_lines=1000000, comment='#', delimiter='\t'):
    # TODO: use delimiter argument
    import sys

    parser = FormatParser()

    entity_factory = parser.parse(format)
    start = time.time()
    sorter = Sorter(entity_factory, max_lines)
    for line in input:
        if not line.startswith(comment):
            break
        output.write(line)
    sorted_iterator = sorter.sort(Iterator(chain([line], input), delimiter=delimiter))
    for i, line in enumerate(sorted_iterator):
        output.write(delimiter.join(line))
        output.write('\n')
    duration = time.time() - start
    output.close()

    n_tmp = ' ' + str(len(sorted_iterator.iterators)) if hasattr(sorted_iterator, 'iterators') else ''
    negator = ' without' if n_tmp == '' else ''
    plural = '' if n_tmp == 1 else 's'
    sys.stderr.write('Sorted {} lines in {:.3f} seconds{} using{} temporary file{}.\n'.format(i, duration, negator, n_tmp, plural))


# CLI


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser("sort is a lhc-python native utility only intended to be used if no other more appropriate solution is available."))


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input', default=None, nargs='?',
            help='input file (default: stdin).')
    add_arg('output', default=None, nargs='?',
            help='output file (default: stdout')
    add_arg('-c', '--comment', default='#',
            help='comment character (default: #)')
    add_arg('-f', '--format', default='s1',
            help='columns and types to extract (default: s1).')
    add_arg('-d', '--delimiter', default='\t',
            help='character delimiting the columns (default: \\t).')
    add_arg('-m', '--max-lines', default=1000000, type=int,
            help='maximum number of lines to sort simultaneously')
    parser.set_defaults(func=init)
    return parser


def init(args):
    import sys
    input = sys.stdin if args.input is None else open(args.input)
    output = sys.stdout if args.output is None else open(args.output, 'w')
    sort(input, output, args.format, args.max_lines, args.comment, args.delimiter)
    input.close()
    output.close()


if __name__ == '__main__':
    import sys
    sys.exit(main())
