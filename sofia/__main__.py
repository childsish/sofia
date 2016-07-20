#!/usr/bin/env python

import argparse
import sys

from sofia.tools import get, build, resolve, execute


def main():
    sys.stderr.write('\n    SoFIA started...\n\n')

    parser = get_parser()
    args = parser.parse_args()
    args.func(args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    build_parser = subparsers.add_parser('build')
    build.define_parser(build_parser)

    execute_parser = subparsers.add_parser('execute')
    execute.define_parser(execute_parser)

    get_parser_ = subparsers.add_parser('get')
    get.define_parser(get_parser_)

    resolve_parser = subparsers.add_parser('resolve')
    resolve.define_parser(resolve_parser)

    return parser


if __name__ == '__main__':
    sys.exit(main())
