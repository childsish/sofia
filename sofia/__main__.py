#!/usr/bin/env python

import argparse
import sys

from sofia.tools import aggregate, info, get, build, resolve


def main():
    sys.stderr.write('\n    SoFIA started...\n\n')

    parser = get_parser()
    args = parser.parse_args()
    args.func(args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    aggregate_parser = subparsers.add_parser('aggregate')
    aggregate.define_parser(aggregate_parser)

    build_parser = subparsers.add_parser('build')
    build.define_parser(build_parser)

    get_parser_ = subparsers.add_parser('get')
    get.define_parser(get_parser_)

    info_parser = subparsers.add_parser('info')
    info.define_parser(info_parser)

    resolve_parser = subparsers.add_parser('resolve')
    resolve.define_parser(resolve_parser)

    return parser


if __name__ == '__main__':
    sys.exit(main())
