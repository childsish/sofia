import argparse
import os

from common import loadPlugins, getProgramDirectory
from ebias.feature import Feature

def main():
    parser = getParser()
    args = parser.parse_args()
    args.func(args)

def getParser():
    parser = argparse.ArgumentParser()
    defineParser(parser)
    return parser

def defineParser(parser):
    parser.add_argument('-v', '--verbose')
    parser.set_defaults(func=list_)

def list_(args):
    program_dir = getProgramDirectory()
    feature_dir = os.path.join(program_dir, 'features')
    feature_types = loadPlugins(feature_dir, Feature)
    
    print '\nAvailable features:\n===================\n'
    for name, type in sorted(feature_types.iteritems(), key=lambda x: x[0]):
        if name in ('resource', 'dynamic_resource', 'static_resource'):
            continue
        print name
        if args.verbose:
            print 'Input\n-----\n%s\n'%', '.join(type.IN)
            print 'Output\n------\n%s\n'%', '.join(type.OUT)
            if hasattr(type, 'DESCRIPTION'):
                print 'Description\n-----------\n%s'%type.DESCRIPTION
            print

if __name__ == '__main__':
    import sys
    sys.exit(main())
