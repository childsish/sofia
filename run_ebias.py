#!/usr/bin/env python

import argparse
import os
import sys

sys.path.append(os.path.realpath(__file__))
from ebias.subcommands import aggregate, list_

def main():
    parser = getParser()
    args = parser.parse_args()
    args.func(args)

def getParser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    aggregate_parser = subparsers.add_parser('aggregate')
    aggregate.defineParser(aggregate_parser)
    
    list_parser = subparsers.add_parser('list')
    list_.defineParser(list_parser)
    
    return parser

if __name__ == '__main__':
    import sys
    sys.exit(main())

