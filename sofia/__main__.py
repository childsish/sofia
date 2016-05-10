#!/usr/bin/env python

import argparse
import sys

from sofia.tools import aggregate, info, get


def main():
    parser = get_parser()
    args = parser.parse_args()
    args.func(args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    aggregate_parser = subparsers.add_parser('aggregate')
    aggregate.define_parser(aggregate_parser)

    get_parser_ = subparsers.add_parser('get')
    get.define_parser(get_parser_)
    
    info_parser = subparsers.add_parser('info')
    info.define_parser(info_parser)
    
    return parser


if __name__ == '__main__':
    sys.exit(main())
