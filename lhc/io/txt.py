import argparse

from txt_ import sorter
from txt_ import extract_typed_columns

def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    subparsers = parser.add_subparsers()

    sort_parser = subparsers.add_parser()
    sorter.define_parser(sort_parser)

    return parser
