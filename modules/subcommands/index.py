import argparse
import os

from modules.resource import Resource
from common import loadPlugins, loadResource

def main():
    parser = getParser()
    args = parser.parse_args()
    args.func(args)

def getParser():
    parser = argparse.ArgumentParser()
    defineParser(parser)
    return parser

def defineParser(parser):
    parser.add_argument('input',
        help='the file to index')
    parser.add_argument('-t', '--type',
        help='the file format of the resource')
    parser.set_defaults(func=index)

def index(args):
    prog_dir = os.path.dirname(os.path.abspath(__file__))
    indir = os.path.join(prog_dir, 'resources')
    parsers = loadPlugins(indir, Resource)
    resource = loadResource(args.input, parsers, args.format)
    resource.index()

if __name__ == '__main__':
    import sys
    sys.exit(main())