import argparse
import os

from common import loadPlugins, getProgramDirectory
from modules.feature import Feature

def main():
    parser = getParser()
    args = parser.parse_args()
    args.func(args)

def getParser():
    parser = argparse.ArgumentParser()
    defineParser(parser)
    return parser

def defineParser(parser):
    parser.set_defaults(func=list_)

def list_(args):
    program_dir = getProgramDirectory()
    feature_dir = os.path.join(program_dir, 'features')
    feature_types = loadPlugins(feature_dir, Feature)
    
    print '\nAvailable features:\n===================\n'
    for name, type in sorted(feature_types.iteritems(), key=lambda x: x[1].__name__):
        if name in ('resource', 'dynamic_resource', 'static_resource'):
            continue
        print '%s (%s):\n\t%s'%(type.__name__, type.NAME, ', '.join(type.RESOURCES))
        if hasattr(type, 'DESCRIPTION'):
            print '\t%s'%type.DESCRIPTION
        print

if __name__ == '__main__':
    import sys
    sys.exit(main())
