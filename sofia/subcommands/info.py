import argparse
import os

from lhc.tools import loadPlugins
from common import getProgramDirectory, loadFeatureHyperGraph
from sofia.features import Feature

def info(args):
    if args.output is None:
        import sys
        args.output = sys.stdout
    else:
        args.output = open(args.output, 'w')
    if args.graph:
        graphFeatures(args)
    else:
        listFeatures(args)
    args.output.close()

def listFeatures(args):
    program_dir = getProgramDirectory()
    feature_dir = os.path.join(program_dir, 'features')
    feature_types = loadPlugins(feature_dir, Feature)
    
    if args.feature is None:
        args.output.write('\nAvailable features:\n===================\n')
        for name, feature_type in sorted(feature_types.iteritems()):
            if name in ('resource', 'dynamic_resource', 'static_resource'):
                continue
            listFeature(feature_type, args)
    else:
        listFeature(feature_types[args.feature], args)

def listFeature(feature, args):
    args.output.write('%s\n'%feature.__name__)
    if args.verbose:
        args.output.write(' Input:\n  %s\n'%', '.join(feature.IN))
        args.output.write(' Output:\n  %s\n'%', '.join(feature.OUT))
        if feature.__doc__ is not None:
            args.output.write(' Description:\n  %s'%feature.__doc__)
        args.output.write('\n')

def graphFeatures(args):
    graph = loadFeatureHyperGraph()
    args.output.write(str(graph))

def main():
    parser = getParser()
    args = parser.parse_args()
    args.func(args)

def getParser():
    parser = argparse.ArgumentParser()
    defineParser(parser)
    return parser

def defineParser(parser):
    parser.add_argument('-g', '--graph', action='store_true',
        help='print out the hyper graph in DOT format (visualise with graphviz)')
    parser.add_argument('-v', '--verbose', action='store_true',
        help='print out descriptions of each feature')
    parser.add_argument('-o', '--output',
        help='specify where to put output')
    parser.add_argument('-f', '--feature',
        help='list a specific feature')
    parser.set_defaults(func=info)
    
if __name__ == '__main__':
    import sys
    sys.exit(main())
