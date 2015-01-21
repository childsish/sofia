import argparse

from txt_ import sorter


def extract_typed_columns(line, columns=((1, str),), sep='\t'):
    parts = line.rstrip('\r\n').split(sep)
    return (t(parts[i]) for i, t in columns)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    subparsers = parser.add_subparsers()

    sort_parser = subparsers.add_parser()
    sorter.define_parser(sort_parser)

    return parser
