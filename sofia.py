#!/usr/bin/env python

import argparse
import os
import sys
program_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.join(program_dir, 'sofia_'))
sys.path.insert(0, os.path.join(program_dir, 'lhc-python'))


from sofia_.subcommands import aggregate, info


def main():
    parser = get_parser()
    args = parser.parse_args()
    args.func(args)


def get_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    aggregate_parser = subparsers.add_parser('aggregate')
    aggregate.define_parser(aggregate_parser)
    
    info_parser = subparsers.add_parser('info')
    info.define_parser(info_parser)
    
    return parser


if __name__ == '__main__':
    sys.exit(main())
