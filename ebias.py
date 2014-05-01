#!/usr/bin/env python
import argparse

from modules.subcommands import aggregate, index, list_

def main(argv):
    parser = getParser()
    args = parser.parse_args()
    args.func(args)

def getParser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    agg_parser = subparsers.add_parser('aggregate')
    aggregate.defineParser(agg_parser)
    idx_parser = subparsers.add_parser('index')
    index.defineParser(idx_parser)
    list_parser = subparsers.add_parser('list')
    list_.defineParser(list_parser)
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
