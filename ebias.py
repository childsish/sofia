#!/usr/bin/env python
import argparse

from collections import OrderedDict
from modules.subcommands.aggregate import aggregate
from modules.subcommands.index import index

def main(argv):
    parser = getParser()
    args = parser.parse_args()
    args.func(args)

def getParser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()
    
    agg_parser = subparsers.add_parser('aggregate')
    agg_parser.add_argument('input', metavar='TARGET',
        help='the file to annotate')
    agg_parser.add_argument('features', nargs='+',
        help='features take the form <feature_name>[:<resource_key>[=<resource_name>]]')
    agg_parser.add_argument('-r', '--resources', nargs='*', action=MakeDict, default={})
    agg_parser.add_argument('-f', '--formats', nargs='*', action=MakeDict, default={})
    agg_parser.set_defaults(func=aggregate)
    
    idx_parser = subparsers.add_parser('index')
    idx_parser.add_argument('input',
        help='the file to index')
    idx_parser.add_argument('-t', '--type',
        help='the file format of the resource')
    idx_parser.set_defaults(func=index)
    return parser

class MakeDict(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, OrderedDict(v.split('=') for v in values))

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
