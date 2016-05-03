#!/usr/bin/env python3
import argparse
import sys

from lhc.random import reservoir


def main():
    args = get_parser().parse_args()
    args.func(args)


def get_parser():
    return define_parser(argparse.ArgumentParser())


def define_parser(parser):
    subparsers = parser.add_subparsers()
    reservoir_parser = subparsers.add_parser('reservoir')
    reservoir.define_parser(reservoir_parser)
    return parser

if __name__ == '__main__':
    sys.exit(main())
