import argparse
import time

from ..iterator import Iterator
from ..entity_parser import EntityParser
from lhc.tools.sorter import Sorter


def sort(input, output, format=('s1',), max_lines=1000000, delimiter='\t'):
    # TODO: use delimiter argument
    import sys

    parser = EntityParser()

    entity_factory = parser.parse_definition(EntityParser.FIELD_DELIMITER.join(format))
    start = time.time()
    sorter = Sorter(entity_factory, max_lines)
    sorted_iterator = sorter.sort(Iterator(input, delimiter=delimiter))
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
    return define_parser(argparse.ArgumentParser("sort is a lhc.python native utility only intended to be used if no other more appropriate solution is available."))


def define_parser(parser):
    add_arg = parser.add_argument
    add_arg('input', default=None, nargs='?',
            help='The input file (default: stdin).')
    add_arg('output', default=None, nargs='?',
            help='The output file (default: stdout')
    add_arg('-f', '--format', nargs='+', default=['s1'],
            help='Which columns and types to extract (default: s1).')
    add_arg('-s', '--delimiter', default='\t',
            help='The character delimiting the columns (default: \\t).')
    add_arg('-m', '--max-lines', default=1000000, type=int,
            help='The maximum number of lines to sort simultaneously')
    parser.set_defaults(func=init)
    return parser


def init(args):
    input = sys.stdin if args.input is None else open(args.input)
    output = sys.stdout if args.output is None else open(args.output, 'w')
    sort(input, output, args.format, args.max_lines, args.delimiter)
    input.close()
    output.close()


if __name__ == '__main__':
    import sys
    sys.exit(main())
