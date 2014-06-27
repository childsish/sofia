import argparse
import os

from ebias.resource import Resource
from common import loadResource, getProgramDirectory
from lhc.tools import loadPlugins

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
    parser.add_argument('-f', '--format',
        help='the file format of the resource')
    parser.set_defaults(func=index)

def index(args):
    program_dir = getProgramDirectory()
    indir = os.path.join(program_dir, 'resources')
    parsers = loadPlugins(indir, Resource)
    resource = loadResource(args.input, parsers, args.format)
    resource.index()

if __name__ == '__main__':
    import sys
    sys.exit(main())
